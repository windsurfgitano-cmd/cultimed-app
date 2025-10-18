from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import os
import re
from datetime import datetime
from functools import lru_cache
import supabase
from supabase import create_client, Client

# ============================================
# CONFIGURACIÓN FLASK
# ============================================
app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURACIÓN SUPABASE
# ============================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://lgicluwwfecrbnfxmbzf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

try:
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error conectando a Supabase: {e}")
    supabase_client = None

# ============================================
# CONSTANTES
# ============================================
BUCKET_NAME = "recetas"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
RUT_CACHE_SIZE = 128

# ============================================
# VALIDADORES
# ============================================
@lru_cache(maxsize=RUT_CACHE_SIZE)
def validar_rut(rut):
    """
    Valida un RUT chileno.
    Formato: XX.XXX.XXX-X o XXXXXXXX-X
    """
    # Limpiar formato
    rut = rut.upper().replace(".", "").replace("-", "").strip()

    # Validar formato básico
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False

    # Separar nԺmeros del dígito verificador
    try:
        numero = int(rut[:-1])
        digito_ingresado = rut[-1]
    except ValueError:
        return False

    # Calcular dígito verificador
    suma = sum(int(d) * (2 + (6 - i % 6)) for i, d in enumerate(str(numero)[::-1]))
    digito_calculado = 11 - (suma % 11)

    if digito_calculado == 11:
        digito_calculado = 0
    elif digito_calculado == 10:
        digito_calculado = "K"
    else:
        digito_calculado = str(digito_calculado)

    return digito_ingresado == str(digito_calculado)

def sanitizar_nombre(nombre):
    """Sanitiza el nombre del archivo."""
    nombre = re.sub(r"[^\w\s.-]", "", nombre)
    nombre = nombre.replace(" ", "_")
    return nombre[:50]  # Máximo 50 caracteres

def archivo_permitido(filename):
    """Valida que el archivo sea permitido."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# RUTAS
# ============================================
HTML_TEMPLATE