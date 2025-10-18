from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head><title>CULTIMED</title></head>
<body><h1>CULTIMED - Registro</h1><p>Application is running!</p></body>
</html>'''

@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
