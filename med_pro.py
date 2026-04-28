import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

# 1. AI sozlamalari
genai.configure(api_key="AIzaSyCe-WC2_SuzsBQchcRg8a-uT52rfHdMyj0")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link rel="icon" type="image/png" href="https://raw.githubusercontent.com/mmuhammadov098/MedAssist/main/logo.png">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/mmuhammadov098/MedAssist/main/logo.png">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-4">
    <div class="max-w-md mx-auto bg-white rounded-2xl shadow-lg overflow-hidden mt-10 text-center">
        <div class="bg-blue-600 p-6 text-white">
            <h1 class="text-2xl font-bold">💊 MedAssist Pro</h1>
        </div>
        <div class="p-6">
            <input type="text" id="drug" class="w-full p-3 border rounded-lg mb-4" placeholder="Dori nomini yozing...">
            <button onclick="askAI()" id="btn" class="w-full bg-blue-600 text-white py-3 rounded-lg font-bold">Ma'lumot olish</button>
            <div id="result" class="mt-6 p-4 border-l-4 border-blue-500 bg-blue-50 hidden">
                <p class="font-bold text-left">Natija:</p>
                <div id="text" class="text-gray-700 mt-2 text-left whitespace-pre-wrap text-sm"></div>
            </div>
        </div>
    </div>
    <script>
        async function askAI() {
            const drug = document.getElementById('drug').value;
            const btn = document.getElementById('btn');
            const resDiv = document.getElementById('result');
            const text = document.getElementById('text');
            if(!drug) return;
            btn.disabled = true; btn.innerText = 'Qidirilmoqda...';
            resDiv.classList.remove('hidden'); text.innerText = 'AI javobini kuting...';
            try {
                const response = await fetch('/get_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({drug: drug})
                });
                const data = await response.json();
                text.innerText = data.result;
            } catch (e) {
                text.innerText = 'Xatolik! Internetni tekshiring.';
            } finally {
                btn.disabled = false; btn.innerText = 'Ma'lumot olish';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.json
    drug = data.get('drug')
    try:
        prompt = f"{drug} dori vositasi haqida o'zbek tilida qisqa va aniq ma'lumot ber (tarkibi, qo'llanilishi)."
        response = model.generate_content(prompt)
        return jsonify({'result': response.text})
    except Exception as e:
        return jsonify({'result': "Xatolik: " + str(e)})

if name == 'main':
    app.run(host='0.0.0.0', port=10000)
