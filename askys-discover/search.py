import os
import gzip
import pickle
from dataclasses import dataclass, field
from typing import Optional

with gzip.open(os.path.join(os.path.dirname(__file__), "normalized_docs.pkl.gz"), "rb") as f:
    md_contents = pickle.load(f)

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
    for content in md_contents:
        if to_search in content['norm_text']:
            match_candidates[content['filename']] = SearchEvidence(
                exact=MatchesInMD(
                    score=1.0,
                    matches=[content['raw_text']]
                )
            )
    return top_results(match_candidates)

def top_results(candidates: dict[str, SearchEvidence]) -> list[SearchResult]:
    results: list[SearchResult] = []
    for filename, evidence in candidates.items():
        if evidence.exact:
            score = evidence.exact.score
            for match_text in evidence.exact.matches:
                results.append(SearchResult(
                    filename=filename,
                    id=len(results) + 1,
                    score=score,
                    content=match_text
                ))
    results.sort(key=lambda x: x.score, reverse=True)
    return results
