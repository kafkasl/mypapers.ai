from flask import Flask, render_template, jsonify, request
import os
from graphql_api import handle_graphql_request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "up"}), 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

# Add the GraphQL endpoint
@app.route('/graphql', methods=['POST'])
def graphql():
    return handle_graphql_request()

if __name__ == "__main__":
    debug = os.getenv("DEBUG")
    port = os.getenv("HTTP_PORT")
    app.run(debug=debug, port=port, use_reloader=False)
