from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# OpenAI kalitini Render'dagi Environment bo'limiga qo'shgan bo'lishingiz shart
openai.api_key = os.getenv("OPENAI_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 10px; margin: 0; }
        .card { background: white; width: 100%; max-width: 400px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; margin-top: 20px; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; }
        .p-3 { padding: 20px; }
        input, button { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 10px; border: 1px solid #ddd; box-sizing: border-box; font-size: 16px; }
        .btn-blue { background: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; }
        .lang-group { display: flex; gap: 5px; margin-bottom: 10px; }
        .btn-lang { flex: 1; border: none; color: white; font-weight: bold; cursor: pointer; padding: 10px; border-radius: 8px; }
        .uz { background: #28a745; } .ru { background: #17a2b8; } .en { background: #343a40; }
        .result { background: #fff; border-left: 5px solid #007bff; padding: 15px; margin-top: 15px; border-radius: 5px; font-size: 14px; line-height: 1.5; min-height: 50px; }
        .blue-t { color: #007bff; font-weight: bold; display: block; margin-top: 10px; }
        .alarm { background: #fff3cd; padding: 15px; border-radius: 15px; margin-top: 20px; border: 1px dashed #ffc107; text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">💊 MedAssist Pro</div>
        <div class="p-3">
            <input type="text" id="drug" placeholder="Dori nomini yozing...">
            <div class="lang-group">
                <button class="btn-lang uz" onclick="setL('uz')">O'ZBEK</button>
                <button class="btn-lang ru" onclick="setL('ru')">РУССКИЙ</button>
                <button class="btn-lang en" onclick="setL('en')">ENGLISH</button>
            </div>
            <button class="btn-blue" onclick="ask()">🔍 QIDIRISH</button>
            <div id="out" class="result">Ma'lumot bu yerda chiqadi...</div>
            <div class="alarm">
                <h4 style="margin:0 0 10px 0">⏰ DORINI ESLATISH</h4>
                <input type="time" id="tm">
                <button onclick="save()" style="background:#28a745; color:white; border:none; margin-top:5px">SAQLASH</button>
                <p id="st" style="font-size:12px; font-weight:bold; margin-top:5px"></p>
            </div>
        </div>
    </div>
    <script>
        let L = 'uz';
        function setL(l) { L = l; alert("Til tanlandi: " + l.toUpperCase()); }
        async function ask() {
            const n = document.getElementById('drug').value;
            if(!n) return;
            document.getElementById('out').innerHTML = "⌛ AI qidirmoqda...";
            try {
                const res = await fetch('/get_drug', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: n, lang: L})
                });
                const data = await res.json();
                let text = data.text.replace(/TARKIBI:/gi, '<span class="blue-t">TARKIBI:</span>')
                                    .replace(/DOZASI:/gi, '<span class="blue-t">DOZASI:</span>')
                                    .replace(/FOYDASI:/gi, '<span class="blue-t">FOYDASI:</span>').replace(/ZARARI:/gi, '<span class="blue-t">ZARARI:</span>');
                document.getElementById('out').innerHTML = text;
            } catch(e) { document.getElementById('out').innerHTML = "❌ Xatolik yuz berdi."; }
        }
        function save() {
            const t = document.getElementById('tm').value;
            if(!t) return;
            localStorage.setItem('med_time', t);
            document.getElementById('st').innerText = "✅ Har kuni " + t + " da eslatiladi";
            alert("Eslatma saqlandi!");
        }
        setInterval(() => {
            const s = localStorage.getItem('med_time');
            if(!s) return;
            const n = new Date();
            const c = n.getHours().toString().padStart(2,'0') + ":" + n.getMinutes().toString().padStart(2,'0');
            if(c === s) alert("🚨 DORINGIZNI ICHING! Vaqt bo'ldi.");
        }, 30000);
        window.onload = () => {
            const s = localStorage.getItem('med_time');
            if(s) document.getElementById('st').innerText = "✅ Har kuni " + s + " da eslatiladi";
        };
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
    prompt = f"Dori: {data['name']}. Til: {data['lang']}. Batafsil: TARKIBI, DOZASI, FOYDASI, ZARARI haqida 3-4 gapdan yoz."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"text": "Xatolik: API kalitni tekshiring."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
