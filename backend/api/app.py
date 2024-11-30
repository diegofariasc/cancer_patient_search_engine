from flask import Flask, jsonify

# Create flask app
app = Flask(__name__)


@app.route("/query", methods=["GET"])
def get_documents():
    documents = [
        {
            "id": 1,
            "document_type": "paper",
            "summary": "Summary 1",
            "document_url": "http://example.com/1",
        },
        {
            "id": 2,
            "document_type": "website",
            "summary": "Summary 2",
            "document_url": "http://example.com/2",
        },
    ]
    return jsonify(documents)
