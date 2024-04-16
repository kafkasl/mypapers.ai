from flask import Flask, render_template, jsonify
import os
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "up"}), 200

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    debug = os.getenv("DEBUG")
    port = os.getenv("HTTP_PORT")

    app.run(debug=debug, port=port, use_reloader=False)