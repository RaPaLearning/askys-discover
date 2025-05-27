from qdrant_client import QdrantClient
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
version = os.environ.get("VER", "v2.0")

def jsonified_result(search_string, results):
    matches = []
    for search_result in results:
        matches.append({
            'filename_no_mdext': search_result.metadata['source'].rsplit('.', 1)[0],
            'match_id': search_result.id,
            'match_score': search_result.score,
            'match_text': search_result.document,
        })
    return jsonify({
            "version": version,
            "to_search": search_string,
            "matches": matches
        })


@app.route("/gita/")
def search_nearest_in_gita():
    to_search = request.args.get('q')
    if to_search:
        qdrant_client = QdrantClient(path='gita_fastembed.qdrant')
        result = qdrant_client.query(
                collection_name='gita_begin_paras',
                query_text=to_search,
                limit=3,
            )
        print(f"Search result: {result}")
        return jsonified_result(to_search, result)
    else:
        return jsonify({
            "version": version,
            "to_search": to_search,
            "errors": 'No search query provided.'
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
