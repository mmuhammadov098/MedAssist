import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f4f8; padding: 15px; font-family: sans-serif; }
        .card { max-width: 400px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.1); background: white; }
        .header { background: #007bff; color: white; padding: 15px; text-align: center; border-radius: 20px 20px 0 0; }
        .med-title { color: #007bff; font-weight: bold; text-transform: uppercase; font-size: 13px; margin-top: 10px; display: block; }
        .med-text { display: block; margin-bottom: 8px; color: #334; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .alarm-area { background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h4>💊 MedAssist Pro</h4></div>
        <div class="p-3">
            <button onclick="startApp()" id="startBtn" class="btn btn-danger w-100 mb-3">🔴 Tizimni faollashtirish (BOSING!)</button>
            
            <input type="text" id="d" class="form-control mb-2" placeholder="Dori nomi...">
            <div class="d-flex gap-2 mb-3">
                <button onclick="ask('uz')" class="btn btn-primary w-100">O'ZBEKCHA</button>
                <button onclick="ask('ru')" class="btn btn-info text-white w-100">РУССКИЙ</button>
            </div>

            <div id="res" class="p-2">Ma'lumot kutilmoqda...</div>

            <div class="alarm-area">
                <h6 class="text-center fw-bold text-success">⏰ ESLATMA VAQTI</h6>
                <div class="d-flex gap-2 my-2">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-success w-100">ESLATMANI YOQISH</button>
                <div id="st" class="small mt-2 text-center fw-bold text-primary"></div>
            </div>
        </div>
    </div>

    <script>
        // Brauzer ovozini va xabarnomasini yoqish
        function startApp() {
            window.speechSynthesis.getVoices();
            Notification.requestPermission();
            document.getElementById('startBtn').className = "btn btn-outline-success w-100 mb-3";
            document.getElementById('startBtn').innerText = "✅ Tizim tayyor";
            alert("Tizim faollashdi! Endi eslatma ishlaydi.");
        }

        async function ask(lang) {
            const name = document.getElementById('d').value;
            if(!name) return;
            document.getElementById('res').innerHTML = "⌛ AI qidirmoqda...";
            
            try {
                const r = await fetch('/api', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, lang})
                });
                const data = await r.json();
                
                let out = "";
                data.text.split('\\n').forEach(line => {
                    if(line.includes(':')) {
                        let [t, ...c] = line.split(':');
                        out += <span class="med-title">${t.trim()}:</span><span class="med-text">${c.join(':').trim()}</span>;
                    }
                });
                document.getElementById('res').innerHTML = out || data.text;
            } catch (e) { document.getElementById('res').innerText = "❌ Xato!"; }
        }function setAlarm() {
            const time = document.getElementById('v').value;
            if(!time) return alert("Vaqtni tanlang!");
            localStorage.setItem('med_alarm', time);
            document.getElementById('st').innerText = "🔔 " + time + " ga qo'yildi";
            alert("Eslatma saqlandi!");
        }

        setInterval(() => {
            const alarm = localStorage.getItem('med_alarm');
            if(!alarm) return;
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(cur === alarm) {
                // 1. Baqirish (Ovoz)
                const speak = new SpeechSynthesisUtterance("Diqqat! Dori ichish vaqti bo'ldi!");
                speak.lang = 'uz-UZ';
                window.speechSynthesis.speak(speak);
                
                // 2. Ekrandagi xabar
                alert("🚨🚨🚨 DORI ICHISH VAQTI!!! 🚨🚨🚨");
                
                // Bir marta chalingach o'chadi
                localStorage.removeItem('med_alarm');
                document.getElementById('st').innerText = "";
            }
        }, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/api', methods=['POST'])
def api():
    d = request.json
    try:
        # AI ga qat'iy 4 ta bandni ko'kda chiqarish uchun buyruq
        p = f"Dori: {d['name']}. Til: {d['lang']}. Faqat 4 band: TARKIBI:, DOZASI:, FOYDASI:, ZARARI:. Qisqa yoz."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": p}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except: return jsonify({"text": "AI xatosi!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
