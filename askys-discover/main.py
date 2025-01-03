import os
from pinecone.grpc import PineconeGRPC as Pinecone
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/gita/")
def search_nearest_in_gita():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_host = os.getenv("PINECONE_HOST")
    version = os.environ.get("VER", "v0.2")
    to_search = request.args.get('q')
    errors = ''
    if not openai_api_key:
        errors += ' no OPENAI_API_KEY.'
    if not pinecone_api_key:
        errors += ' no PINECONE_API_KEY.'
    if not pinecone_host:
        errors += ' no PINECONE_HOST'
    return jsonify({
        "version": version,
        "search-string": to_search,
        "errors": errors
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
