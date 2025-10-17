from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

# 1. INICIALIZACIÓN DE FLASK
# ==================================
app = Flask(__name__)
CORS(app)

# 2. CONFIGURACIÓN DE SUPABASE (Variables de Entorno)
# =======================================================
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lgicluwwfecrbnfxmbzf.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '') # La KEY debe estar en tus variables de entorno de Vercel

sb = None
if SUPABASE_KEY:
    try:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error al inicializar Supabase: {e}")

# 3. LÓGICA DE LA APLICACIÓN (Funciones)
# =========================================
def validar_rut(rut):
    """Función para validar un RUT chileno."""
    rut = rut.upper().replace(".", "").replace("-", "")
    if len(rut) < 2:
        return False
    try:
        num = int(rut[:-1])
        dv = rut[-1]
        s = 0
        m = 2
        while num > 0:
            s += (num % 10) * m
            num //= 10
            m += 1
            if m > 7:
                m = 2
        dv_calc = 11 - (s % 11)
        if dv_calc == 11:
            dv_calc = 0
        elif dv_calc == 10:
            dv_calc = "K"
        return str(dv_calc) == dv
    except:
        return False

# 4. PLANTILLA HTML CON JAVASCRIPT INTEGRADO
# ==================================================
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CULTIMED - Registro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Segoe UI", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .container { background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; animation: slideIn 0.5s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; border-radius: 15px 15px 0 0; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .form-container { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input, textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1em; transition: all 0.2s ease-in-out; }
        input:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        .file-upload { border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; background: #f9f9f9; transition: all 0.2s ease-in-out; }
        .file-upload:hover { background: rgba(102,126,234,0.05); }
        .file-upload.error { border-color: #dc3545; background: #f8d7da; } /* Estilo de error para el campo de archivo */
        #fileInput { display: none; }
        .file-name { color: #667eea; margin-top: 10px; font-weight: 500; }
        .rut-status { margin-top: 5px; font-size: 0.9em; font-weight: 500; height: 1em; }
        .rut-valid { color: #28a745; }
        .rut-invalid { color: #dc3545; }
        button { width: 100%; padding: 14px; border: none; border-radius: 8px; font-size: 1.1em; cursor: pointer; font-weight: 600; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-top: 20px; transition: all 0.3s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102,126,234,0.3); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
        .message { margin-top: 20px; padding: 15px; border-radius: 8px; display: none; font-weight: 500; }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; display: block; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; display: block; }
        .loading { display: none; text-align: center; color: #667eea; font-weight: 500; margin-top: 15px;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💊 CULTIMED</h1>
            <p>Registro de Clientes - Receta Médica</p>
        </div>
        <div class="form-container">
            <form id="form" novalidate> <div class="form-group">
                    <label for="nombre">Nombre Completo *</label>
                    <input type="text" id="nombre" name="nombre" required placeholder="Juan Pérez">
                </div>
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" name="email" required placeholder="juan.perez@example.com">
                </div>
                <div class="form-group">
                    <label for="telefono">Teléfono *</label>
                    <input type="tel" id="telefono" name="telefono" required placeholder="+56 9 1234 5678">
                </div>
                <div class="form-group">
                    <label for="cedula">RUT *</label>
                    <input type="text" id="cedula" name="cedula" required placeholder="12.345.678-9" maxlength="12">
                    <div class="rut-status" id="rutStatus"></div>
                </div>
                <div class="form-group">
                    <label>Receta (PDF/JPG/PNG, max 5MB) *</label>
                    <div class="file-upload" id="uploadArea">
                        <p>Arrastra tu archivo aquí o haz clic para seleccionar</p>
                        <input type="file" id="fileInput" name="fileInput" accept=".pdf,.jpg,.jpeg,.png" required>
                        <div class="file-name" id="fileName"></div>
                    </div>
                </div>
                <button type="submit" id="btn">Enviar Registro</button>
                <div class="loading" id="loading">Enviando...</div>
                <div class="message" id="msg"></div>
            </form>
        </div>
    </div>

    <script>
        const form = document.getElementById('form');
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const msgDiv = document.getElementById('msg');
        const fileNameDiv = document.getElementById('fileName');

        // Simular clic en el input oculto
        uploadArea.addEventListener('click', () => fileInput.click());

        // Mostrar nombre del archivo seleccionado
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                fileNameDiv.textContent = fileInput.files[0].name;
                uploadArea.classList.remove('error'); // Quita el error si el usuario selecciona un archivo
                msgDiv.style.display = 'none';
            }
        });

        // Validar el formulario antes de enviarlo
        form.addEventListener('submit', function(event) {
            // Prevenir el envío por defecto para validar primero
            event.preventDefault();

            let isValid = true;
            
            // Validar que el archivo no esté vacío
            if (fileInput.files.length === 0) {
                isValid = false;
                uploadArea.classList.add('error');
                msgDiv.textContent = 'Por favor, selecciona un archivo de receta para continuar.';
                msgDiv.className = 'message error';
            } else {
                uploadArea.classList.remove('error');
            }

            // Aquí podrías agregar otras validaciones para los campos de texto si quisieras

            if (isValid) {
                // Si todo está bien, podrías mostrar un mensaje de 'enviando...'
                // y luego enviar el formulario con AJAX o de forma normal.
                console.log('Formulario válido, listo para enviar.');
                // form.submit(); // Descomenta esta línea si quieres hacer un envío de página completa
                
                // Por ahora, solo mostraremos un mensaje de éxito simulado
                msgDiv.textContent = '¡Formulario enviado con éxito! (Simulación)';
                msgDiv.className = 'message success';
            }
        });
    </script>
</body>
</html>
"""

# 5. RUTAS DE LA API (Endpoints)
# =================================
@app.route('/')
def index():
    """Ruta principal que muestra el formulario HTML."""
    return render_template_string(HTML)

@app.route('/validar-rut', methods=['POST'])
def handle_validar_rut():
    """Ruta para validar el RUT desde el frontend."""
    rut = request.json.get('rut')
    if not rut:
        return jsonify({'valido': False, 'error': 'RUT no proporcionado'}), 400
    
    es_valido = validar_rut(rut)
    return jsonify({'valido': es_valido})

# (Aquí puedes agregar la ruta para manejar el envío del formulario a Supabase)

# 6. EJECUCIÓN DE LA APLICACIÓN
# =================================
# Esta parte permite ejecutar el servidor localmente para pruebas.
if __name__ == '__main__':
    app.run(debug=True)
