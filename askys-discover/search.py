import os
import gzip
import pickle
from dataclasses import dataclass, field
from typing import Optional
from rapidfuzz import fuzz
from aksharamukha import transliterate # type: ignore
from rank_bm25 import BM25Okapi # type: ignore

with gzip.open(os.path.join(os.path.dirname(__file__), "normalized_docs.pkl.gz"), "rb") as f:
    md_contents = pickle.load(f)
bm25_md_contents = BM25Okapi([content.split(" ") for content in (c['norm_text'] for c in md_contents)])

@dataclass
class MatchesInMD:
    score: float = 0.0
    matches: list[str] = field(default_factory=list[str])

@dataclass
class SearchEvidence:
    exact: Optional[MatchesInMD] = None
    bm25: Optional[MatchesInMD] = None
    semantic: Optional[MatchesInMD] = None
    fuzzy: Optional[MatchesInMD] = None
    score: float = 0.0
    matches: set[str] = field(default_factory=set[str])

@dataclass
class SearchResult:
    filename: str
    id: int
    score: float
    content: str

class MatchCandidates:
    def __init__(self, to_search: str) -> None:
        self.to_search = to_search
        self.bm25_weight = 1 if len(to_search.split(" ")) <= 4 else 0.5
        self.candidates: dict[str, SearchEvidence] = {}
    def __getitem__(self, filename: str) -> SearchEvidence:
        return self.candidates[filename]
    def __setitem__(self, filename: str, value: SearchEvidence) -> None:
        self.candidates[filename] = value
    def __contains__(self, filename: str) -> bool:
        return filename in self.candidates
    def __len__(self) -> int:
        return len(self.candidates)
    def evidence_for_file(self, filename: str) -> SearchEvidence:
        if filename not in self.candidates:
            self.candidates[filename] = SearchEvidence()
        return self.candidates[filename]
    def fill_score_per_file(self) -> None:
        for _, evidence in self.candidates.items():
            if evidence.exact:
                evidence.score += evidence.exact.score
                evidence.matches.update(evidence.exact.matches)
            if evidence.fuzzy:
                evidence.score += evidence.fuzzy.score
                evidence.matches.update(evidence.fuzzy.matches)
            if evidence.bm25:
                evidence.score += evidence.bm25.score * self.bm25_weight
                evidence.matches.update(evidence.bm25.matches)
    
    def trim_contents(self, search_results: list[SearchResult]) -> None:
        for result in search_results:
            paras = result.content.split('\n\n')
            para_scores = [fuzz.partial_ratio(self.to_search, para) for para in paras]
            max_idx = para_scores.index(max(para_scores))
            result.content = paras[max_idx]

    def top_results(self) -> list[SearchResult]:
        self.fill_score_per_file()
        results: list[SearchResult] = []
        for filename, evidence in self.candidates.items():
            score = evidence.score
            for match_text in evidence.matches:
                results.append(SearchResult(
                    filename=filename,
                    id=len(results) + 1,
                    score=score,
                    content=match_text
                ))
        results.sort(key=lambda x: x.score, reverse=True)
        top_ranked = list(filter(lambda x: x.score >= 0.85, results[:3]))  # threshold for overall match score
        self.trim_contents(top_ranked)
        return top_ranked

def normalize(text: str) -> str:
    return " ".join(
        text.lower()
            .replace("\r", " ")
            .replace("\n", " ")
            .split()
    )

def search(search_string: str, try_second_best: bool=True) -> list[SearchResult]:
    to_search = normalize(search_string)
    matches = MatchCandidates(to_search)  # key is filename
    for content in md_contents:
        if to_search in content['norm_text']:
            matches.evidence_for_file(content['filename']).exact = MatchesInMD(
                    score=1.0,
                    matches=[content['raw_text']]
                )
        fuzzy_evidence = fuzzy_match(to_search, content)
        if fuzzy_evidence:
            matches.evidence_for_file(content['filename']).fuzzy = fuzzy_evidence
    file_matches_bm25 = bm25_file_matches(to_search)
    for filename in file_matches_bm25:
        matches.evidence_for_file(filename).bm25 = file_matches_bm25[filename]
    top_matches = matches.top_results()
    if len(top_matches) == 0 and try_second_best:
        second_try = search_for_second_try(to_search)
        if second_try != to_search:
            return search(second_try, try_second_best=False)
    return top_matches

def fuzzy_match(to_search: str, content: dict[str, str]) -> MatchesInMD | None:
    ratio = fuzz.partial_ratio(to_search, content['norm_text'])
    if ratio >= 35:
        return MatchesInMD(
            score=ratio / 100.0,
            matches=[content['raw_text']]
        )
    else:
        return None

def bm25_file_matches(to_search: str) -> dict[str, MatchesInMD]:
    tokenized_query = to_search.split(" ")
    bm25_scores: list[int] = bm25_md_contents.get_scores(tokenized_query) # type: ignore
    max_bm25_score = max(bm25_scores) if len(bm25_scores) > 0 else 0
    if max_bm25_score < 0.1:
        return {}
    norm_bm25_scores = [(score / max_bm25_score) for score in bm25_scores]
    matched_files: dict[str, MatchesInMD] = {}
    for idx, score in enumerate(norm_bm25_scores):
        if score > 0.55:  # threshold for normalized BM25 match
            matched_files[md_contents[idx]['filename']] = MatchesInMD(
                score=score,
                matches=[md_contents[idx]['raw_text']]
            )
    return matched_files

def search_for_second_try(original_search: str) -> str:
    return transliterate.process('autodetect', 'HK', original_search) # type: ignore
