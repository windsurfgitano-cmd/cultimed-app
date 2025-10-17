from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from datetime import datetime
from supabase import create_client

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://lgicluwwfecrbnfxmbzf.supabase.co"
SUPABASE_KEY = "sbp_84fa682bc6d4f5c0692d797bd5a43f29d0a2bbda"
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def validar_rut(rut):
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

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CULTIMED - Registro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .container { background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; animation: slideIn 0.5s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .form-container { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input, textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1em; }
        input:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        .file-upload { border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; background: #f9f9f9; }
        .file-upload:hover { background: rgba(102,126,234,0.05); }
        #fileInput { display: none; }
        .file-name { color: #667eea; margin-top: 10px; font-weight: 500; }
        .rut-status { margin-top: 5px; font-size: 0.9em; font-weight: 500; }
        .rut-valid { color: #28a745; }
        .rut-invalid { color: #dc3545; }
        button { width: 100%; padding: 14px; border: none; border-radius: 8px; font-size: 1.1em; cursor: pointer; font-weight: 600; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-top: 20px; transition: all 0.3s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102,126,234,0.3); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .message { margin-top: 20px; padding: 15px; border-radius: 8px; display: none; font-weight: 500; }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; display: block; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; display: block; }
        .loading { display: none; text-align: center; color: #667eea; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💊 CULTIMED</h1>
            <p>Registro de Clientes - Receta Medica</p>
        </div>
        <div class="form-container">
            <form id="form">
                <div class="form-group">
                    <label for="nombre">Nombre Completo *</label>
                    <input type="text" id="nombre" name="nombre" required placeholder="Juan Perez">
                </div>
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" name="email" required placeholder="correo@example.com">
                </div>
                <div class="form-group">
                    <label for="telefono">Telefono *</label>
                    <input type="tel" id="telefono" name="telefono" required placeholder="+56 9 1234 5678">
                </div>
                <div class="form-group">
                    <label for="cedula">RUT (auto-formato) *</label>
                    <input type="text" id="cedula" name="cedula" required placeholder="12345678-9" maxlength="12">
                    <div class="rut-status" id="rutStatus"></div>
                </div>
                <div class="form-group">
                    <label>Receta Medica (PDF, JPG, PNG - max 5MB) *</label>
                    <div class="file-upload" id="upload">
                        <p>Arrastra archivo o haz click para seleccionar</p>
                        <input type="file" id="fileInput" name="fileInput" accept=".pdf,.jpg,.jpeg,.png" required>
                        <div class="file-name" id="fileName"></div>
                    </div>
                </div>
                <button type="submit" id="btn">Enviar Registro</button>
                <div class="loading" id="loading">Guardando...</div>
                <div class="message" id="msg"></div>
            </form>
        </div>
    </div>

    <script>
        const form = document.getElementById('form');
        const cedula = document.getElementById('cedula');
        const rutStatus = document.getElementById('rutStatus');
        const upload = document.getElementById('upload');
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        const msg = document.getElementById('msg');
        const btn = document.getElementById('btn');
        const loading = document.getElementById('loading');

        cedula.addEventListener('input', (e) => {
            let val = e.target.value.toUpperCase().replace(/[^0-9K-]/g, '');
            if (val.length >= 2) {
                const num = val.slice(0, -1).replace(/[^0-9]/g, '');
                const dv = val.slice(-1);
                if (num.length >= 6) {
                    e.target.value = num.slice(0, -6) + '.' + num.slice(-6, -3) + '.' + num.slice(-3) + '-' + dv;
                }
            }
            validarRUT(e.target.value);
        });

        function validarRUT(rut) {
            const clean = rut.toUpperCase().replace(/[^0-9K]/g, '');
            if (clean.length < 2) {
                rutStatus.textContent = '';
                return false;
            }
            try {
                let num = parseInt(clean.slice(0, -1));
                const dv = clean.slice(-1);
                let s = 0, m = 2;
                while (num > 0) {
                    s += (num % 10) * m;
                    num = Math.floor(num / 10);
                    m = m === 7 ? 2 : m + 1;
                }
                const dvCalc = (11 - (s % 11)) % 11 === 10 ? 'K' : ((11 - (s % 11)) % 11).toString();
                const valido = dvCalc === dv;
                rutStatus.textContent = valido ? 'Valido' : 'Invalido';
                rutStatus.className = 'rut-status ' + (valido ? 'rut-valid' : 'rut-invalid');
                return valido;
            } catch (e) {
                rutStatus.textContent = 'Invalido';
                rutStatus.className = 'rut-status rut-invalid';
                return false;
            }
        }

        upload.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                fileName.textContent = file.name + ' (' + sizeMB + 'MB)';
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!validarRUT(cedula.value)) { showMsg('RUT invalido', 'error'); return; }
            if (!fileInput.files.length) { showMsg('Selecciona un archivo', 'error'); return; }

            btn.disabled = true;
            loading.style.display = 'block';
            msg.style.display = 'none';

            const fd = new FormData(form);
            try {
                const res = await fetch('/api/registro', { method: 'POST', body: fd });
                const data = await res.json();
                
                if (res.ok) {
                    showMsg('Registro guardado! Revisa tu email', 'success');
                    form.reset();
                    fileName.textContent = '';
                    rutStatus.textContent = '';
                } else {
                    showMsg('Error: ' + (data.message || data.error || 'Intenta de nuevo'), 'error');
                }
            } catch (e) {
                showMsg('Error de conexion: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        });

        function showMsg(text, type) {
            msg.textContent = text;
            msg.className = 'message ' + type;
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        cedula = request.form.get('cedula', '').strip()
        archivo = request.files.get('fileInput')

        if not all([nombre, email, telefono, cedula, archivo]):
            return jsonify({'error': 'Faltan datos', 'message': 'Completa todos los campos'}), 400

        if not validar_rut(cedula):
            return jsonify({'error': 'RUT invalido', 'message': 'Verifica el RUT'}), 400

        ext = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
        if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
            return jsonify({'error': 'Formato no permitido', 'message': 'Solo PDF, JPG, PNG'}), 400

        archivo.seek(0, 2)
        size = archivo.tell()
        if size > 5 * 1024 * 1024:
            return jsonify({'error': 'Archivo > 5MB', 'message': 'Max 5MB'}), 400
        archivo.seek(0)

        file_content = archivo.read()
        file_path = f"{cedula}/{datetime.now().isoformat()}_{archivo.filename}"
        
        sb.storage.from_("recetas").upload(file_path, file_content)

        datos = {
            'cedula': cedula,
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'archivo': file_path,
            'estado': 'pendiente',
            'created_at': datetime.now().isoformat()
        }
        sb.table('clientes').insert(datos).execute()

        return jsonify({'success': True, 'message': 'Registro guardado correctamente'}), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e), 'message': 'Error en servidor'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'app': 'CULTIMED'}), 200

if __name__ == '__main__':
    app.run(debug=False)
