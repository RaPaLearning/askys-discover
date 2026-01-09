import os
from flask import Flask, request, jsonify
from search import search, SearchResult

app = Flask(__name__)


def jsonified_result(search_string: str, results: list[SearchResult]):
    matches: list[dict[str, object]] = []
    for search_result in results:
        matches.append({
            'filename_no_mdext': search_result.filename.rsplit('.', 1)[0],
            'match_id': search_result.id,
            'match_score': search_result.score,
            'match_text': search_result.content,
        })
    return jsonify({
            "version": os.environ.get("VER", "v2.0"),
            "to_search": search_string,
            "matches": matches
        })


@app.route("/gita/")
def search_nearest_in_gita():
    to_search = request.args.get('q')
    if to_search:
        return jsonified_result(to_search, search(to_search))
    else:
        return jsonify({
            "version": os.environ.get("VER", "v2.0"),
            "to_search": to_search,
            "errors": 'No search query provided.'
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
