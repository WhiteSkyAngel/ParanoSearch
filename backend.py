from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # En développement uniquement

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    parano_mode = request.args.get('parano', 'false') == 'true'
    
    try:
        # Mode Parano : Fausses requêtes
        if parano_mode:
            requests.get(f"https://duckduckgo.com/?q=fake_query_{hash(keyword)}")
        
        # Vraie requête
        response = requests.get(f"https://api.duckduckgo.com/?q={keyword}&format=json&ia=web")
        data = response.json()
        
        # Extraction des résultats
        results = []
        for result in data.get('RelatedTopics', []):
            if 'Text' in result and 'FirstURL' in result:
                results.append({
                    "title": result['Text'], 
                    "link": result['FirstURL']
                })
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/suggest')
def suggest():
    query = request.args.get('q', '')
    try:
        response = requests.get(f"https://duckduckgo.com/ac/?q={query}")
        return jsonify([{'phrase': item['phrase']} for item in response.json()])
    except Exception as e:
        return jsonify([])

@app.route('/parano')
def parano():
    query = request.args.get('q', '')
    try:
        # Simule une requête sans stocker de réponse
        requests.get(f"https://duckduckgo.com/?q={query}&ia=web")
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)