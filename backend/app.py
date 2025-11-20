from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/')
def home():
    return jsonify({"message": "Backend is running!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"data": "Sample data from backend"})

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.get_json()
    return jsonify({"received": data, "status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

