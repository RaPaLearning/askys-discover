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

def normalize(text: str) -> str:
    return " ".join(
        text.lower()
            .replace("\r", " ")
            .replace("\n", " ")
            .split()
    )

def search(search_string: str, try_second_best: bool=True) -> list[SearchResult]:
    to_search = normalize(search_string)
    match_candidates: dict[str, SearchEvidence] = {}  # key is filename
    def evidence_for_file(filename: str) -> SearchEvidence:
        if filename not in match_candidates:
            match_candidates[filename] = SearchEvidence()
        return match_candidates[filename]
    for content in md_contents:
        if to_search in content['norm_text']:
            evidence_for_file(content['filename']).exact = MatchesInMD(
                    score=1.0,
                    matches=[content['raw_text']]
                )
        fuzzy_evidence = fuzzy_match(to_search, content)
        if fuzzy_evidence:
            evidence_for_file(content['filename']).fuzzy = fuzzy_evidence
    file_matches_bm25 = bm25_file_matches(to_search)
    for filename in file_matches_bm25:
        evidence_for_file(filename).bm25 = file_matches_bm25[filename]
    if match_candidates == {} and try_second_best:
        second_try = search_for_second_try(to_search)
        if second_try != to_search:
            return search(second_try, try_second_best=False)
    fill_score_per_file(match_candidates)
    return top_results(match_candidates)

def top_results(candidates: dict[str, SearchEvidence]) -> list[SearchResult]:
    results: list[SearchResult] = []
    for filename, evidence in candidates.items():
        score = evidence.score
        for match_text in evidence.matches:
            results.append(SearchResult(
                filename=filename,
                id=len(results) + 1,
                score=score,
                content=match_text
            ))
    results.sort(key=lambda x: x.score, reverse=True)
    return results # TODO return top 3 results[:3] after including semantics

def fill_score_per_file(candidates: dict[str, SearchEvidence]) -> None:
    for _, evidence in candidates.items():
        if evidence.exact:
            evidence.score += evidence.exact.score
            evidence.matches.update(evidence.exact.matches)
        if evidence.fuzzy:
            evidence.score += evidence.fuzzy.score
            evidence.matches.update(evidence.fuzzy.matches)
        if evidence.bm25:
            evidence.score += evidence.bm25.score
            evidence.matches.update(evidence.bm25.matches)
        # TODO: Additional scoring logic for semantics can be added here

def fuzzy_match(to_search: str, content: dict[str, str]) -> MatchesInMD | None:
    ratio = fuzz.partial_ratio(to_search, content['norm_text'])
    if ratio >= 85:
        return MatchesInMD(
            score=ratio / 100.0,
            matches=[content['raw_text']]
        )
    else:
        return None

def bm25_file_matches(to_search: str) -> dict[str, MatchesInMD]:
    tokenized_query = to_search.split(" ")
    bm25_scores: list[int] = bm25_md_contents.get_scores(tokenized_query) # type: ignore
    matched_files: dict[str, MatchesInMD] = {}
    for idx, score in enumerate(bm25_scores):
        if score > 1.2:  # threshold for BM25 match
            matched_files[md_contents[idx]['filename']] = MatchesInMD(
                score=score,
                matches=[md_contents[idx]['raw_text']]
            )
    return matched_files

def search_for_second_try(original_search: str) -> str:
    return transliterate.process('autodetect', 'HK', original_search) # type: ignore
