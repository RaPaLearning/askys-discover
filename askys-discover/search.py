import os
import gzip
import pickle
from dataclasses import dataclass, field
from typing import Optional
from rapidfuzz import fuzz
# from rank_bm25 import BM25Okapi

with gzip.open(os.path.join(os.path.dirname(__file__), "normalized_docs.pkl.gz"), "rb") as f:
    md_contents = pickle.load(f)
# bm25_md_contents = BM25Okapi([content.split(" ") for content in (c['norm_text'] for c in md_contents)])

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
    matches: list[str] = field(default_factory=list[str])

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

def search(search_string: str) -> list[SearchResult]:
    to_search = normalize(search_string)
    match_candidates: dict[str, SearchEvidence] = {}  # key is filename
    def search_evidence_for_file(filename: str) -> SearchEvidence:
        if filename not in match_candidates:
            match_candidates[filename] = SearchEvidence()
        return match_candidates[filename]
    for content in md_contents:
        if to_search in content['norm_text']:
            search_evidence_for_file(content['filename']).exact = MatchesInMD(
                    score=1.0,
                    matches=[content['raw_text']]
                )
        fuzzy_evidence = fuzzy_match(to_search, content)
        if fuzzy_evidence:
            search_evidence_for_file(content['filename']).fuzzy = fuzzy_evidence
    fill_score_per_file(match_candidates)
    return top_results(match_candidates)

def fuzzy_match(to_search: str, content: dict[str, str]) -> MatchesInMD | None:
    ratio = fuzz.partial_ratio(to_search, content['norm_text'])
    if ratio >= 85:
        return MatchesInMD(
            score=ratio / 100.0,
            matches=[content['raw_text']]
        )
    else:
        return None
    
def fill_score_per_file(candidates: dict[str, SearchEvidence]) -> None:
    for _, evidence in candidates.items():
        if evidence.exact:
            evidence.score += evidence.exact.score
            evidence.matches.extend(evidence.exact.matches)
        if evidence.fuzzy:
            evidence.score += evidence.fuzzy.score
            evidence.matches.extend(evidence.fuzzy.matches)
        # TODO: Additional scoring logic for other match types can be added here

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
    return results
