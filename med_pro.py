import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# API ulanishi
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 20px; font-family: sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        #res { background: #fff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; margin: 15px 0; min-height: 60px; }
        .alarm-card { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h4>💊 MedAssist Pro AI</h4></div>
        <div class="p-4 bg-white">
            <input type="text" id="dori" class="form-control mb-3" placeholder="Dori nomi...">
            <div class="d-flex gap-1 mb-3">
                <button onclick="ask('uz')" class="btn btn-primary w-100">O'zbek</button>
                <button onclick="ask('ru')" class="btn btn-info text-white w-100">Русский</button>
            </div>
            
            <div id="res">Ma'lumot kutilmoqda...</div>

            <div class="alarm-card">
                <h6 class="text-center">⏰ Dori vaqtini belgilash</h6>
                <div class="d-flex gap-2 mb-2">
                    <input type="time" id="vqt" class="form-control">
                    <input type="number" id="kun" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-warning w-100 fw-bold">Eslatmani Yoqish</button>
                <div id="status" class="small mt-2 text-center fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        async function ask(l) {
            const n = document.getElementById('dori').value;
            if(!n) return alert("Dori nomini yozing!");
            document.getElementById('res').innerHTML = "⌛ AI o'ylamoqda...";
            
            try {
                const r = await fetch('/data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({n: n, l: l})
                });
                const d = await r.json();
                document.getElementById('res').innerHTML = d.t;
            } catch(e) {
                document.getElementById('res').innerHTML = "❌ Xatolik! API kalitni tekshiring.";
            }
        }

        function setAlarm() {
            const v = document.getElementById('vqt').value;
            const k = document.getElementById('kun').value;
            if(!v || !k) return alert("To'liq to'ldiring!");
            
            const end = new Date().getTime() + (k * 24 * 60 * 60 * 1000);
            localStorage.setItem('alarm', JSON.stringify({v: v, e: end}));
            document.getElementById('status').innerText = "🔔 Eslatma o'rnatildi: " + v;
            alert("Budilnik yoqildi!");
        }

        setInterval(() => {
            const a = JSON.parse(localStorage.getItem('alarm'));
            if(!a) return;
            if(new Date().getTime() > a.e) return localStorage.removeItem('alarm');
            
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');if(cur === a.v) {
                const speak = new SpeechSynthesisUtterance("Vaqt bo'ldi! Dori ichish vaqtingiz bo'ldi!");
                window.speechSynthesis.speak(speak);
                alert("⏰ VAQT BO'LDI! Dori iching!");
            }
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/data', methods=['POST'])
def data():
    req = request.json
    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{req['n']} haqida {req['l']} tilida ma'lumot ber."}]
        )
        return jsonify({"t": chat.choices[0].message.content})
    except Exception as e:
        return jsonify({"t": f"API Xatosi: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
