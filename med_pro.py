from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 15px; margin: 0; }
        .card { background: white; max-width: 500px; margin: auto; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; }
        .p-3 { padding: 20px; }
        input { width: 100%; padding: 12px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        
        .lang-group { display: flex; gap: 5px; margin-bottom: 15px; }
        .btn-lang { flex: 1; padding: 10px; border: none; border-radius: 8px; cursor: pointer; color: white; font-weight: bold; }
        
        /* Tillar ranglari siz aytgandek: */
        .uz { background: #28a745; } /* Yashil */
        .ru { background: #ffc107; color: black; } /* Sariq */
        .en { background: #dc3545; } /* Qizil */
        
        .btn-main { width: 100%; padding: 15px; background: #007bff; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .result { background: #fff; border-left: 5px solid #007bff; padding: 15px; margin-top: 15px; font-size: 14px; line-height: 1.6; }
        .blue-t { color: #0056b3; font-weight: bold; display: block; margin-top: 10px; }
        .warning { background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; margin-top: 15px; font-size: 12px; text-align: center; border: 1px solid #ffeeba; }
        
        .alarm-box { background: #e7f3ff; padding: 15px; border-radius: 15px; margin-top: 20px; border: 2px dashed #007bff; text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">🛡 MedAssist Pro</div>
        <div class="p-3">
            <input type="text" id="drug" placeholder="Dori nomini yozing...">
            <div class="lang-group">
                <button class="btn-lang uz" onclick="setL('uz')">O'ZBEK</button>
                <button class="btn-lang ru" onclick="setL('ru')">РУССКИЙ</button>
                <button class="btn-lang en" onclick="setL('en')">ENGLISH</button>
            </div>
            <button class="btn-main" onclick="ask()">🔍 QIDIRISH</button>
            <div id="out" class="result">Ma'lumot bu yerda chiqadi...</div>
            <div class="warning">
                ⚠️ DIQQAT: MA'LUMOTLAR AI TOMONIDAN BERILGAN. DORINI ICHISHDAN OLDIN ALBATTA SHIFOKOR BILAN MASLAHATLASHING!
            </div>
            <div class="alarm-box">
                <h4>⏰ ESLATMA O'RNATISH</h4>
                <input type="time" id="tm">
                <button onclick="save()" style="background:#28a745; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">SAQLASH</button>
                <p id="st"></p>
            </div>
        </div>
    </div>

    <script>
        let L = 'uz';
        function setL(l) { L = l; alert(l.toUpperCase() + " tanlandi"); }
        async function ask() {
            const n = document.getElementById('drug').value;
            if(!n) return;
            document.getElementById('out').innerText = "⌛ Qidirilmoqda...";
            const res = await fetch('/get_drug', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: n, lang: L})
            });
            const data = await res.json();
            let t = data.text.replace(/TARKIBI:/g, '<span class="blue-t">🧪 TARKIBI:</span>').replace(/DOZASI:/g, '<span class="blue-t">⚖️ DOZASI:</span>')
                             .replace(/FOYDASI:/g, '<span class="blue-t">✅ FOYDASI:</span>')
                             .replace(/ZARARI:/g, '<span class="blue-t">❌ ZARARI:</span>');
            document.getElementById('out').innerHTML = t;
        }
        function save() {
            const t = document.getElementById('tm').value;
            if(!t) return;
            localStorage.setItem('med_time', t);
            document.getElementById('st').innerText = "🔔 Eslatma " + t + " ga qo'yildi!";
            if(Notification.permission !== 'granted') Notification.requestPermission();
        }
        setInterval(() => {
            const s = localStorage.getItem('med_time');
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            if(s === cur) {
                alert("🚨 VAQT BO'LDI! DORINGIZNI ICHING! (Shifokor tavsiyasiga amal qiling)");
                new Notification("🚨 MedAssist: Dori ichish vaqti!");
            }
        }, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/get_drug', methods=['POST'])
def get_drug():
    data = request.json
    prompt = f"{data['name']} dorisi haqida {data['lang']} tilida TARKIBI:, DOZASI:, FOYDASI: va ZARARI: bo'limlari bilan ma'lumot ber."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return jsonify({"text": response.choices[0].message.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
