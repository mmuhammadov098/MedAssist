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
        body { background: #f4f7f6; padding: 15px; font-family: 'Segoe UI', sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.08); background: white; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        
        /* 4 ta asosiy bo'lim uchun ko'k sarlavha */
        .med-label { color: #007bff; font-weight: 800; font-size: 14px; text-transform: uppercase; margin-top: 12px; display: block; border-bottom: 1px solid #eef2f7; }
        .med-value { color: #334155; font-size: 15px; margin-bottom: 8px; display: block; line-height: 1.4; }
        
        #res { min-height: 50px; padding: 10px; }
        .alarm-box { background: #e8f5e9; padding: 20px; border-radius: 15px; border: 2px solid #c8e6c9; margin-top: 20px; }
        .btn-success { background: #2e7d32; border: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist Pro</h3></div>
        <div class="p-4">
            <button onclick="initAudio()" class="btn btn-outline-primary btn-sm w-100 mb-3">🔔 Eslatmani faollashtirish (Bosing)</button>
            
            <input type="text" id="d" class="form-control mb-3" placeholder="Dori nomi...">
            <div class="d-flex gap-2">
                <button onclick="getMed('uz')" class="btn btn-primary w-100">O'zbekcha</button>
                <button onclick="getMed('ru')" class="btn btn-info text-white w-100">Русский</button>
            </div>

            <div id="res" class="mt-3">Ma'lumot kutilmoqda...</div>

            <div class="alarm-box">
                <h6 class="text-center fw-bold text-success">⏰ DORI ICHISH VAQTI</h6>
                <div class="d-flex gap-2 my-2">
                    <input type="time" id="t" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setupAlarm()" class="btn btn-success w-100">Eslatmani saqlash</button>
                <div id="msg" class="small mt-2 text-center text-success fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        // Brauzer ovoz chiqarishi uchun ruxsat
        function initAudio() {
            window.speechSynthesis.getVoices();
            alert("Eslatma tizimi tayyor!");
        }

        async function getMed(lang) {
            const d = document.getElementById('d').value;
            if(!d) return;
            const res = document.getElementById('res');
            res.innerHTML = "⌛ AI tayyorlamoqda...";
            
            try {
                const response = await fetch('/get', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: d, lang: lang})
                });
                const data = await response.json();
                
                // Matnni 4 ta bo'limga bo'lib ko'kda chiqarish
                let lines = data.text.split('\\n');
                let html = "";
                lines.forEach(l => {
                    if(l.includes(':')) {
                        let [title, ...content] = l.split(':');
                        html += <span class="med-label">${title.trim()}:</span>;html += <span class="med-value">${content.join(':').trim()}</span>;
                    }
                });
                res.innerHTML = html || data.text;
            } catch { res.innerHTML = "❌ Xato!"; }
        }

        function setupAlarm() {
            const time = document.getElementById('t').value;
            if(!time) return alert("Vaqtni kiriting!");
            localStorage.setItem('med_time', time);
            document.getElementById('msg').innerText = "✅ Eslatma " + time + " ga qo'yildi";
        }

        // Har 15 soniyada tekshirish
        setInterval(() => {
            const savedTime = localStorage.getItem('med_time');
            if(!savedTime) return;
            
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(cur === savedTime) {
                // 1. Ovozli xabar
                let talk = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                talk.lang = 'uz-UZ';
                window.speechSynthesis.speak(talk);
                
                // 2. Ekrandagi ogohlantirish
                alert("🚨🚨🚨 VAQT BO'LDI! DORINGIZNI ICHING! 🚨🚨🚨");
                
                // Bir marta ishlagach to'xtatish (ixtiyoriy)
                localStorage.removeItem('med_time');
                document.getElementById('msg').innerText = "";
            }
        }, 15000);
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/get', methods=['POST'])
def get_med():
    data = request.json
    try:
        # AI ga qat'iy buyruq: faqat 4 ta qisqa band
        prompt = f"Dori: {data['name']}. Til: {data['lang']}. Faqat 4 ta bandda juda qisqa javob ber: 1.Tarkibi:, 2.Dozasi:, 3.Foydasi:, 4.Zarari:. Boshqa so'z qo'shma."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except: return jsonify({"text": "Xato yuz berdi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
