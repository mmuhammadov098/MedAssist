import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Dori vositalari bazasi (Mustaqil baza)
MED_DATABASE = {
    "yodamarin": {
        "uz": "Yodamarin - yod tanqisligini oldini olish uchun dori. Tarkibi: Kaliy yodid.",
        "ru": "Йодомарин - препарат для профилактики дефицита йода. Состав: Калия йодид.",
        "en": "Yodamarin - a drug for the prevention of iodine deficiency. Composition: Potassium iodide."
    },
    "analgin": {
        "uz": "Analgin - og'riq qoldiruvchi va isitma tushiruvchi dori. Tarkibi: Metamizol natriy.",
        "ru": "Анальгин - анальгезирующее ненаркотическое средство. Состав: Метамизол натрия.",
        "en": "Analgin - an analgesic and antipyretic drug. Composition: Metamizole sodium."
    }
}

# HTML Kod - Logotip va chiroyli interfeys bilan
HTML_CODE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    
    <link rel="icon" href="https://img.icons8.com/color/96/pill.png" type="image/png">
    <link rel="apple-touch-icon" href="https://img.icons8.com/color/192/pill.png">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .card { max-width: 550px; margin: auto; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none; overflow: hidden; }
        .header { background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); color: white; padding: 25px; text-align: center; }
        .btn-lang { width: 32%; font-weight: bold; border-radius: 12px; padding: 12px; }
        #result { background: white; border: 1px solid #eee; padding: 20px; border-radius: 15px; min-height: 150px; margin-top: 20px; line-height: 1.8; color: #333; font-size: 16px; }
        .disclaimer { font-size: 12px; color: #d93025; text-align: center; margin-top: 15px; font-weight: bold; background: #fbe9e7; padding: 10px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <img src="https://img.icons8.com/color/96/pill.png" width="50" height="50" alt="Logo" class="mb-2">
            <h3>MedAssist Pro</h3>
            <p class="mb-0 small">Professional Tibbiy Ma'lumotnoma</p>
        </div>
        <div class="p-4 bg-white">
            <input type="text" id="drugInput" class="form-control form-control-lg mb-3 shadow-sm" placeholder="Dori nomini yozing...">
            <div class="d-flex justify-content-between mb-3">
                <button onclick="getInfo('uz')" class="btn btn-primary btn-lang">O'zbek</button>
                <button onclick="getInfo('ru')" class="btn btn-info text-white btn-lang">Русский</button>
                <button onclick="getInfo('en')" class="btn btn-dark btn-lang">English</button>
            </div>
            <div id="result">Natija bu yerda chiqadi.</div>
            <p class="disclaimer">⚠️ DIQQAT: SHIFOKOR BILAN MASLAHATLASHING!</p>
        </div>
    </div>
    <script>
        function getInfo(lang) {
            const drug = document.getElementById('drugInput').value.toLowerCase().trim();
            if(!drug) { alert("Iltimos, dori nomini yozing!"); return; }
            
            fetch('/get_data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: drug, lang: lang})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('result').innerText = data.text;
            })
            .catch(err => {
                document.getElementById('result').innerText = "Tarmoq xatosi.";
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)@app.route('/get_data', methods=['POST'])
def get_data():
    data = request.json
    name = data.get('name')
    lang = data.get('lang')
    
    # Baza dan qidirish
    drug_info = MED_DATABASE.get(name)
    if drug_info:
        return jsonify({"text": drug_info.get(lang)})
    else:
        # Topilmasa javob
        messages = {
            'uz': "Kechirasiz, bu dori bazada topilmadi.",
            'ru': "Извините, этот препарат не найден.",
            'en': "Sorry, this drug was not found."
        }
        return jsonify({"text": messages.get(lang, "Not found.")})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
