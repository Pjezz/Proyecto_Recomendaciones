from neo4j import GraphDatabase
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from models.graph import get_recommendations

NEO4J_URI = "bolt://localhost:7687"  # O "neo4j+s://<host>:<port>" si estás usando Aura
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "estructura"  
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

app = Flask(__name__)
CORS(app)

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    data = request.json
    brand = data.get('brand')
    budget = data.get('budget')
    transmission = data.get('transmission')
    types = data.get('types', [])

    results = get_recommendations(brand, budget, transmission, types)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
