import os
import openai
from pinecone.grpc import PineconeGRPC as Pinecone
from flask import Flask, request, jsonify

app = Flask(__name__)
version = os.environ.get("VER", "v0.3")


def generate_query_embedding(query):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    embedding = response.data[0].embedding
    return embedding


def query_pinecone_index(embedding, index, top_k=3):
    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )
    return response


def jsonified_result(search_string, results):
    matches = []
    if 'matches' in results:
        for i, result in enumerate(results['matches']):
            match_id = result['id']
            match_metadata = result.get('metadata', {})
            commentary_chunks = []
            if match_metadata:
                commentary_chunks = match_metadata.get('commentary_chunks', 'No commentary chunks available')
            matches.append({
                'filename_no_mdext': match_id.rsplit('-', 1)[0],
                'match_id': match_id,
                'match_score': result['score'],
                'commentary_chunks': commentary_chunks
            })
    return jsonify({
            "version": version,
            "to_search": search_string,
            "matches": matches
        })


@app.route("/gita/")
def search_nearest_in_gita():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_host = os.getenv("PINECONE_HOST")
    to_search = request.args.get('q')
    errors = ''
    if not openai_api_key:
        errors += ' no OPENAI_API_KEY.'
    if not pinecone_api_key:
        errors += ' no PINECONE_API_KEY.'
    if not pinecone_host:
        errors += ' no PINECONE_HOST'
    if not errors and to_search:
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(host=pinecone_host)
        embedding = generate_query_embedding(to_search)
        result = query_pinecone_index(embedding, index)
        return jsonified_result(to_search, result)
    else:
        return jsonify({
            "version": version,
            "to_search": to_search,
            "errors": errors
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
