import sys
import os
import pandas as pd
from rapidfuzz import fuzz

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'askys-discover'))
from search import md_contents, bm25_md_contents

def compute_scores(query: str) -> pd.DataFrame:
    scoring_df = pd.DataFrame(columns=['filename', 'exact', 'fuzzy', 'bm25'])
    scoring_df['filename'] = [content['filename'] for content in md_contents]
    scoring_df['exact'] = [int(query in content['norm_text']) for content in md_contents]
    scoring_df['fuzzy'] = [fuzz.partial_ratio(query, content['norm_text'])/100 for content in md_contents]
    tokenized_query = query.split(" ")
    bm25_scores: list[int] = bm25_md_contents.get_scores(tokenized_query) # type: ignore
    scoring_df['bm25'] = bm25_scores

    return scoring_df

def write_query_scores(query: str) -> None:
    scores_df = compute_scores(query)
    output_file = f"sco_{query.replace(' ', '_')}.csv"
    scores_df.to_csv(output_file, index=False)
    print(f"Scores written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python raw_scoring_illustration.py <search_query>")
        sys.exit(1)
    user_query = sys.argv[1]
    write_query_scores(user_query)