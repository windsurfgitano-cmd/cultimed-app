from flask import Flask, render_template_string, request, jsonify
from supabase import create_client
from datetime import datetime

app = Flask(__name__)

SUPABASE_URL = "https://lgicluwwfecrbnfxmbzf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxnaWNsdXd3ZmVjcmJuZnhtYnpmIiwicm5sZSI6ImFub24iLCJpYXQiOjE3Mjc5MjU5MjMsImV4cCI6MjA0MzUwMTkyM30.x0xKgAu7wHlKNZkMPxK8vJZmO52F6m7VfpwvJvQoHcw"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CULTIMED - Registro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; color: white; }
        .logo { font-size: 50px; margin-bottom: 10px; }
        .header h1 { font-size: 2em; margin-bottom: 5px; }
        .form-container { padding: 40px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .required::after { content: ' *'; color: #e74c3c; }
        input, textarea { width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1em; font-family: inherit; }
        input:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        .file-area { border: 3px dashed #667eea; border-radius: 10px; padding: 30px; text-align: center; cursor: pointer; background: #f8f9ff; transition: all 0.3s; }
        .file-area:hover { border-color: #764ba2; background: #f0f2ff; }
        .file-area input { display: none; }
        .buttons { display: flex; gap: 15px; margin-top: 30px; }
        button { flex: 1; padding: 14px; border: none; border-radius: 10px; font-size: 1em; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .btn-submit { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-submit:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102,126,234,0.3); }
        .btn-reset { background: #f0f2ff; color: #667eea; border: 2px solid #667eea; }
        .alert { padding: 15px; border-radius: 10px; margin-bottom: 20px; display: none; }
        .alert.show { display: block; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        textarea { min-height: 80px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">💊</div>
            <h1>CULTIMED</h1>
            <p>Sistema de Registro de Clientes</p>
        </div>
        <div class="form-container">
            <div id="alert" class="alert"></div>
            <form id="registroForm">
                <div class="form-group">
                    <label for="nombre" class="required">Nombre Completo</label>
                    <input type="text" id="nombre" name="nombre" placeholder="Juan Pérez" required>
                </div>
                <div class="form-group">
                    <label for="email" class="required">Email</label>
                    <input type="email" id="email" name="email" placeholder="juan@example.com" required>
                </div>
                <div class="form-group">
                    <label for="telefono" class="required">Teléfono</label>
                    <input type="tel" id="telefono" name="telefono" placeholder="+56 9 1234 5678" required>
                </div>
                <div class="form-group">
                    <label for="cedula" class="required">Cédula / RUT</label>
                    <input type="text" id="cedula" name="cedula" placeholder="12.345.678-9" required>
                </div>
                <div class="form-group">
                    <label for="receta" class="required">Cargar Receta Médica</label>
                    <div class="file-area" id="uploadArea">
                        <div style="font-size: 2.5em; margin-bottom: 10px;">📁</div>
                        <div style="color: #667eea; font-weight: 600;">Arrastra tu receta aquí</div>
                        <div style="color: #999; font-size: 0.9em; margin-top: 5px;">o haz clic para seleccionar</div>
                        <input type="file" id="receta" name="receta" accept=".pdf,.jpg,.jpeg,.png" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="doctor">Médico Prescriptor</label>
                    <input type="text" id="doctor" name="doctor" placeholder="Dr. Carlos López">
                </div>
                <div class="form-group">
                    <label for="notas">Notas Adicionales</label>
                    <textarea id="notas" name="notas" placeholder="Información adicional..."></textarea>
                </div>
                <div class="buttons">
                    <button type="submit" class="btn-submit" id="submitBtn">Registrarse</button>
                    <button type="reset" class="btn-reset">Limpiar</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('receta');
        const form = document.getElementById('registroForm');
        const alertBox = document.getElementById('alert');
        const submitBtn = document.getElementById('submitBtn');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.style.background = '#e8e9ff'; });
        uploadArea.addEventListener('dragleave', () => { uploadArea.style.background = '#f8f9ff'; });
        uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.style.background = '#f8f9ff'; fileInput.files = e.dataTransfer.files; });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            submitBtn.disabled = true;
            submitBtn.textContent = 'Registrando...';

            try {
                const response = await fetch('/api/registro', { method: 'POST', body: formData });
                const data = await response.json();

                if (response.ok) {
                    alertBox.textContent = '✅ ¡Registro exitoso! Gracias por usar CULTIMED';
                    alertBox.className = 'alert show alert-success';
                    form.reset();
                } else {
                    alertBox.textContent = '❌ Error: ' + (data.error || 'No se pudo registrar');
                    alertBox.className = 'alert show alert-error';
                }
            } catch (error) {
                alertBox.textContent = '❌ Error de conexión: ' + error.message;
                alertBox.className = 'alert show alert-error';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Registrarse';
                setTimeout(() => alertBox.classList.remove('show'), 5000);
            }
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        cedula = request.form.get('cedula')
        doctor = request.form.get('doctor', '')
        notas = request.form.get('notas', '')
        archivo = request.files.get('receta')

        if not all([nombre, email, telefono, cedula, archivo]):
            return jsonify({'error': 'Faltan campos obligatorios'}), 400

        if not supabase:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500

        try:
            filename = f"{cedula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.filename}"
            file_path = f"recetas/{filename}"
            file_data = archivo.read()

            supabase.storage.from_("recetas").upload(file_path, file_data, {"content-type": archivo.content_type})
            
            supabase.table("clientes").insert({
                "cedula": cedula,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "doctor": doctor,
                "notas": notas,
                "archivo": file_path,
                "created_at": datetime.now().isoformat()
            }).execute()

            return jsonify({'success': True, 'message': 'Registro exitoso'}), 200
        except Exception as db_error:
            return jsonify({'error': f'Error al guardar: {str(db_error)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registros', methods=['GET'])
def get_registros():
    try:
        if not supabase:
            return jsonify({'error': 'Conexión no disponible'}), 500
        response = supabase.table("clientes").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'app': 'CULTIMED'}), 200

if __name__ == '__main__':
    app.run(debug=False)
