import os
from pinecone.grpc import PineconeGRPC as Pinecone
from flask import Flask

app = Flask(__name__)


@app.route("/")
def search_nearest_in_gita():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_host = os.getenv("PINECONE_HOST")
    name = os.environ.get("VER", "v0.1")
    errors = ''
    if not openai_api_key:
        errors += ' no OPENAI_API_KEY.'
    if not pinecone_api_key:
        errors += ' no PINECONE_API_KEY.'
    if not pinecone_host:
        errors += ' no PINECONE_HOST'
    return f"askys-discover {name}\n{errors}\n"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
