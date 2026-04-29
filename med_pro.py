import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding: 15px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { max-width: 420px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        .result-box { background: white; padding: 15px; border-radius: 12px; margin-top: 15px; min-height: 120px; border: 1px solid #e0e0e0; }
        .label-blue { color: #007bff; font-weight: bold; display: block; margin-top: 8px; font-size: 0.9rem; text-transform: uppercase; }
        .value-text { display: block; margin-bottom: 5px; color: #333; font-size: 1rem; line-height: 1.4; }
        .alarm-zone { background: #e3f2fd; padding: 15px; border-radius: 15px; border: 2px dashed #007bff; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist Pro</h3></div>
        <div class="p-3">
            <button onclick="initSystem()" id="initBtn" class="btn btn-danger w-100 mb-3">🔔 TIZIMNI AKTIVLASHTIRISH</button>
            
            <input type="text" id="drugName" class="form-control mb-2" placeholder="Dori nomini yozing...">
            <div class="btn-group w-100 mb-3">
                <button onclick="fetchInfo('uz')" class="btn btn-primary">O'ZBEK</button>
                <button onclick="fetchInfo('ru')" class="btn btn-info text-white">РУССКИЙ</button>
                <button onclick="fetchInfo('en')" class="btn btn-dark">ENGLISH</button>
            </div>

            <div id="display" class="result-box">Ma'lumot bu yerda chiqadi...</div>

            <div class="alarm-zone">
                <h6 class="text-center fw-bold">⏰ DORINI ESLATISH</h6>
                <div class="d-flex gap-2 my-2">
                    <input type="time" id="alarmTime" class="form-control">
                    <input type="number" id="days" class="form-control" placeholder="Kun">
                </div>
                <button onclick="saveAlarm()" class="btn btn-success w-100">ESLATMANI YOQISH</button>
                <div id="alarmStatus" class="small mt-2 text-center text-primary fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        function initSystem() {
            window.speechSynthesis.getVoices();
            document.getElementById('initBtn').className = "btn btn-outline-success w-100 mb-3";
            document.getElementById('initBtn').innerText = "✅ Tizim tayyor";
            alert("Ovozli eslatmalar faollashdi!");
        }

        async function fetchInfo(lang) {
            const name = document.getElementById('drugName').value;
            if(!name) return;
            const box = document.getElementById('display');
            box.innerHTML = "⌛ AI qidirmoqda...";
            
            try {
                const response = await fetch('/api/get-info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, lang})
                });
                const data = await response.json();
                
                let formatted = "";
                data.text.split('\\n').forEach(line => {
                    if(line.includes(':')) {let [title, ...content] = line.split(':');
                        formatted += <span class="label-blue">${title.trim()}:</span>;
                        formatted += <span class="value-text">${content.join(':').trim()}</span>;
                    }
                });
                box.innerHTML = formatted || data.text;
            } catch (e) { box.innerText = "❌ Xatolik yuz berdi!"; }
        }

        function saveAlarm() {
            const t = document.getElementById('alarmTime').value;
            if(!t) return;
            localStorage.setItem('med_reminder_time', t);
            document.getElementById('alarmStatus').innerText = "🔔 Reja: " + t;
            alert("Eslatma saqlandi!");
        }

        setInterval(() => {
            const setTime = localStorage.getItem('med_reminder_time');
            if(!setTime) return;
            const now = new Date();
            const nowStr = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(nowStr === setTime) {
                let msg = new SpeechSynthesisUtterance("Diqqat, dori ichish vaqti bo'ldi!");
                msg.lang = 'uz-UZ';
                window.speechSynthesis.speak(msg);
                alert("🚨 DORI ICHISH VAQTI!!! 🚨");
                localStorage.removeItem('med_reminder_time');
                document.getElementById('alarmStatus').innerText = "";
            }
        }, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/get-info', methods=['POST'])
def get_info():
    req = request.json
    try:
        p = f"Dori: {req['name']}. Til: {req['lang']}. Faqat 4 punkt: TARKIBI:, DOZASI:, FOYDASI:, ZARARI:. Qisqa va aniq yoz."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": p}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except: return jsonify({"text": "AI bog'lanishda xato!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
