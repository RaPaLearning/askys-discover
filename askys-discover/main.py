import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from search import search, SearchResult

APP_VERSION = "v4.0"

app = Flask(__name__)
CORS(app)
prev_token_used = ''

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
            "version": APP_VERSION,
            "to_search": search_string,
            "matches": matches
        })

@app.route("/gita/")
def search_nearest_in_gita():
    global prev_token_used
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401)
    token = auth_header.split(' ')[1]
    if token == prev_token_used or len(token) < 30:
        abort(401)
    prev_token_used = token

    to_search = request.args.get('q')
    if to_search:
        return jsonified_result(to_search, search(to_search))
    else:
        return jsonify({
            "version": APP_VERSION,
            "to_search": to_search,
            "errors": 'No search query provided.'
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
