from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
import base64
import hashlib
import json
from functools import wraps
import io

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ADMIN_USER = 'admin'
ADMIN_PASS = 'cultimed2024'

HTML_CLIENTE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CULTIMED - Registro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .form-container { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        .rut-valid { border-color: #28a745 !important; }
        .rut-invalid { border-color: #dc3545 !important; }
        .file-upload {
            border: 2px dashed #667eea;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .file-upload:hover { background: rgba(102,126,234,0.05); }
        .file-upload.dragover { background: rgba(102,126,234,0.1); border-color: #764ba2; }
        #fileInput { display: none; }
        .file-info { color: #667eea; margin-top: 10px; font-weight: 500; }
        .progress-bar { width: 100%; height: 4px; background: #e0e0e0; border-radius: 4px; margin-top: 20px; display: none; }
        .progress-bar.active { display: block; }
        .progress { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px; width: 0%; animation: progress 3s ease-in-out; }
        @keyframes progress { from { width: 0%; } to { width: 100%; } }
        .button-group { display: flex; gap: 10px; margin-top: 30px; }
        button { flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 1em; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        .btn-submit { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-submit:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102,126,234,0.3); }
        .btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-reset { background: #f0f0f0; color: #333; }
        .btn-reset:hover { background: #e0e0e0; }
        .message { margin-top: 20px; padding: 15px; border-radius: 8px; display: none; animation: fadeIn 0.3s ease-out; }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; display: block; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; display: block; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💊 CUMTIMED</h1>
            <p>Registro de Clientes - Receta Médica</p>
        </div>
        <div class="form-container">
            <form id="form">
                <div class="form-group">
                    <label for="nombre">Nombre Completo *</label>
                    <input type="text" id="nombre" name="nombre" required placeholder="Juan Pérez">
                </div>
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" name="email" required placeholder="correo@example.com">
                </div>
                <div class="form-group">
                    <label for="telefono">Teléfono *</label>
                    <input type="tel" id="telefono" name="telefono" required placeholder="+56 9 1234 5678">
                </div>
                <div class="form-group">
                    <label for="rut">RUT/Cédula *</label>
                    <input type="text" id="rut" name="rut" required placeholder="12.345.678-9">
                </div>
                <div class="form-group">
                    <label>Receta Médica (PDF, JPG, PNG - máx 5MB) *</label>
                    <div class="file-upload" id="upload">
                        <p>📎 Arrastra archivo o haz click</p>
                        <input type="file" id="fileInput" name="fileInput" accept=".pdf,.jpg,.jpeg,.png" required>
                        <div class="file-info" id="fileInfo"></div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="doctor">Médico Prescriptor (Opcional)</label>
                    <input type="text" id="doctor" name="doctor" placeholder="Dr. Juan Sánchez">
                </div>
                <div class="form-group">
                    <label for="notas">Notas Adicionales (Opcional)</label>
                    <textarea id="notas" name="notas" placeholder="Información adicional..." rows="3"></textarea>
                </div>
                <div class="progress-bar" id="progressBar"><div class="progress"></div></div>
                <div class="button-group">
                    <button type="submit" class="btn-submit" id="submitBtn">📤 Enviar</button>
                    <button type="reset" class="btn-reset" id="resetBtn">🔄 Limpiar</button>
                </div>
                <div class="message" id="msg"></div>
            </form>
        </div>
    </div>

    <script>
        const form = document.getElementById('form');
        const upload = document.getElementById('upload');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const msg = document.getElementById('msg');
        const progressBar = document.getElementById('progressBar');
        const submitBtn = document.getElementById('submitBtn');
        const rutInput = document.getElementById('rut');

        function validateRUT(rut) {
            rut = rut.replace(/[^0-9kK]/g, '');
            if (!rut) return false;
            const rutNum = rut.slice(0, -1);
            const dv = rut.slice(-1).toUpperCase();
            let sum = 0, mult = 2;
            for (let i = rutNum.length - 1; i >= 0; i--) {
                sum += parseInt(rutNum[i]) * mult;
                mult = mult === 9 ? 2 : mult + 1;
            }
            const resto = 11 - (sum % 11);
            const dvCalc = resto === 11 ? '0' : resto === 10 ? 'K' : resto.toString();
            return dvCalc === dv;
        }

        rutInput.addEventListener('input', (e) => {
            const valid = validateRUT(e.target.value);
            e.target.classList.toggle('rut-valid', valid);
            e.target.classList.toggle('rut-invalid', !valid && e.target.value.length > 5);
        });

        upload.addEventListener('click', () => fileInput.click());
        upload.addEventListener('dragover', (e) => { e.preventDefault(); upload.classList.add('dragover'); });
        upload.addEventListener('dragleave', () => upload.classList.remove('dragover'));
        upload.addEventListener('drop', (e) => {
            e.preventDefault();
            upload.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            updateFileInfo();
        });
        fileInput.addEventListener('change', updateFileInfo);

        function updateFileInfo() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const size = (file.size / 1024 / 1024).toFixed(2);
                fileInfo.textContent = `✅ ${file.name} (${size} MB)`;
            } else {
                fileInfo.textContent = '';
            }
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) {
                showMsg('❌ Selecciona un archivo', 'error');
                return;
            }
            if (!validateRUT(rutInput.value)) {
                showMsg('❌ RUT inválido', 'error');
                return;
            }

            submitBtn.disabled = true;
            progressBar.classList.add('active');

            const fd = new FormData(form);
            try {
                const res = await fetch('/api/registro', { method: 'POST', body: fd });
                if (res.ok) {
                    const data = await res.json();
                    showMsg('✅ ¡Registro guardado! Nos contactaremos pronto.', 'success');
                    form.reset();
                    fileInfo.textContent = '';
                    rutInput.classList.remove('rut-valid');
                } else {
                    const err = await res.json();
                    showMsg('❌ Error: ' + (err.message || err.error || 'Error desconocido'), 'error');
                }
            } catch (e) {
                showMsg('❌ Error de conexión: ' + e.message, 'error');
            } finally {
                submitBtn.disabled = false;
                progressBar.classList.remove('active');
            }
        });

        function showMsg(text, type) {
            msg.textContent = text;
            msg.className = 'message ' + type;
        }
    </script>
</body>
</html>"""

registros_db = {}

@app.route('/')
def index():
    return render_template_string(HTML_CLIENTE)

@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        rut = request.form.get('rut')
        doctor = request.form.get('doctor', '')
        notas = request.form.get('notas', '')
        archivo = request.files.get('fileInput')

        if not all([nombre, email, telefono, rut, archivo]):
            return jsonify({'error': 'Faltan datos', 'message': 'Completa todos los campos obligatorios'}), 400

        if archivo.filename == '':
            return jsonify({'error': 'Sin archivo', 'message': 'Selecciona un archivo de receta'}), 400

        allowed = {'pdf', 'jpg', 'jpeg', 'png'}
        ext = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
        if ext not in allowed:
            return jsonify({'error': 'Formato inválido', 'message': 'Solo PDF, JPG, PNG permitidos'}), 400

        archivo.seek(0, 2)
        size = archivo.tell()
        if size > 5 * 1024 * 1024:
            return jsonify({'error': 'Archivo muy grande', 'message': 'Máximo 5MB'}), 400
        archivo.seek(0)

        datos = {
            'rut': rut,
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'doctor': doctor,
            'notas': notas,
            'fecha': datetime.now().isoformat()
        }
        
        registros_db[rut] = datos
        
        return jsonify({'success': True, 'message': 'Registro guardado correctamente'}), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'app': 'CULTIMED', 'status': 'OK'}), 200

if __name__ == '__main__':
    app.run(debug=False)