from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from datetime import datetime
from functools import lru_cache
import os

app = Flask'__name__')
CORS(app)

# Configuración esde variables de entorno
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lgicluwwfecrbnfxmbzf.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Constantes
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
STORAGE_BUCKET = 'recetas'
TABLE_NAME = 'clientes'

# Inicializar Supabase con manejo de errores
sb = None
try:
    if SUPABASE_KEY:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase conectado")
except Exception as e:
    print(f"✗ Error Supabase: {e}")

@lru_cache(maxsize=128)
def validar_rut(rut: str) -> bool:
   "..."

HTML_PAGE = """<!DOCTYPE html>..."""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/registro',
methods=['POST'])
def registro():
    ...

@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
