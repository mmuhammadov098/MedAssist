import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

# 1. AI sozlamalari (Eng barqaror versiya)
genai.configure(api_key="AIzaSyCe-WC2_SuzsBQchcRg8a-uT52rfHdMyj0")
model = genai.GenerativeModel('gemini-pro') # 'gemini-1.5-flash' o'rniga 'gemini-pro' ishlatamiz

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f0f4f8; }
        .card { background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="p-4 md:p-10">
    <div class="max-w-md mx-auto card overflow-hidden">
        <div class="bg-blue-600 p-6 text-white text-center">
            <h1 class="text-2xl font-bold">💊 MedAssist Pro</h1>
        </div>
        <div class="p-6">
            <label class="block font-bold mb-2">Dori nomi:</label>
            <input type="text" id="drugName" class="w-full p-3 border rounded-lg mb-4" placeholder="Masalan: Analgin">
            
            <button onclick="askAI()" id="btn" class="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition">
                AI dan ma'lumot olish
            </button>

            <div id="result" class="mt-6 p-4 border-l-4 border-blue-500 bg-blue-50 hidden">
                <p class="font-bold text-gray-700">Natija:</p>
                <div id="aiResponse" class="text-gray-600 mt-2 whitespace-pre-wrap text-sm"></div>
            </div>
        </div>
    </div>

    <script>
        async function askAI() {
            const drug = document.getElementById('drugName').value;
            const btn = document.getElementById('btn');
            const resultDiv = document.getElementById('result');
            const responseDiv = document.getElementById('aiResponse');

            if(!drug) return alert('Dori nomini yozing!');

            btn.disabled = true;
            btn.innerText = 'Qidirilmoqda...';
            resultDiv.classList.remove('hidden');
            responseDiv.innerText = 'AI javobini kuting...';

            try {
                const response = await fetch('/get_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({drug: drug})
                });
                const data = await response.json();
                responseDiv.innerText = data.result;
            } catch (e) {
                responseDiv.innerText = 'Xatolik yuz berdi. Qaytadan urinib koʻring.';
            } finally {
                btn.disabled = false;
                btn.innerText = 'AI dan ma'lumot olish';
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
        # Promptni o'zbek tilida so'rashni tayinlaymiz
        prompt = f"{drug} dori vositasi haqida o'zbek tilida batafsil ma'lumot ber (qo'llanilishi, dozasi, nojo'ya ta'sirlari)."
        response = model.generate_content(prompt)
        return jsonify({'result': response.text})
    except Exception as e:
        return jsonify({'result': str(e)})

if name == 'main':
    app.run(host='0.0.0.0', port=10000)
