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
        body { background: linear-gradient(180deg, #f0f4f8 0%, #d9e2ec 100%); min-height: 100vh; padding: 15px; }
        .card { max-width: 450px; margin: auto; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: none; background: white; overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        #res { background: #fff; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; margin: 15px 0; min-height: 50px; }
        .res-title { color: #007bff; font-weight: bold; display: block; margin-top: 10px; text-transform: uppercase; font-size: 13px; }
        .res-text { display: block; margin-bottom: 10px; color: #334155; }
        /* Eslatma qismi yashil */
        .alarm-section { background: #e8f5e9; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; }
        .btn-success { background: #2e7d32; border: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist Pro</h3></div>
        <div class="p-4">
            <button onclick="reqNotif()" class="btn btn-outline-primary btn-sm w-100 mb-3">🔔 Bildirishnomaga ruxsat berish</button>
            <input type="text" id="d" class="form-control mb-3" placeholder="Dori nomi (masalan: Paracetamol)">
            <div class="d-flex gap-2 mb-3">
                <button onclick="ask('uz')" class="btn btn-primary w-100">O'zbek</button>
                <button onclick="ask('ru')" class="btn btn-info text-white w-100">Русский</button>
            </div>

            <div id="res">Ma'lumot bu yerda chiqadi...</div>

            <div class="alarm-section mt-4">
                <h6 class="text-center fw-bold mb-3">⏰ Dori ichish vaqti</h6>
                <div class="d-flex gap-2 mb-3">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-success w-100 shadow-sm">Eslatmani yoqish</button>
                <div id="st" class="small mt-2 text-center text-success fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        function reqNotif() {
            Notification.requestPermission().then(p => { if(p==='granted') alert("Ruxsat berildi!"); });
        }

        async function ask(lang) {
            const name = document.getElementById('d').value;
            if(!name) return alert("Dori nomini yozing!");
            document.getElementById('res').innerHTML = "⌛ AI qidirmoqda...";
            
            try {
                const response = await fetch('/get_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, lang})
                });
                const data = await response.json();
                
                // Natijani formatlash
                let html = "";
                data.text.split('\\n').forEach(line => {
                    if(line.includes(':')) {
                        let [t, ...c] = line.split(':');
                        html += <span class="res-title">${t.trim()}:</span><span class="res-text">${c.join(':').trim()}</span>;
                    } else if (line.trim().length > 0) {html += <span class="res-text">${line}</span>;
                    }
                });
                document.getElementById('res').innerHTML = html || data.text;
            } catch (e) { document.getElementById('res').innerHTML = "⚠️ Xato! Internetni tekshiring."; }
        }

        function setAlarm() {
            const time = document.getElementById('v').value;
            const days = document.getElementById('k').value;
            if(!time || !days) return alert("Vaqt va kunni yozing!");
            localStorage.setItem('med_alarm', JSON.stringify({time, expire: Date.now() + (days * 86400000)}));
            document.getElementById('st').innerText = "✅ " + time + " ga qo'yildi";
            alert("Eslatma saqlandi!");
        }

        setInterval(() => {
            const alarm = JSON.parse(localStorage.getItem('med_alarm'));
            if(!alarm) return;
            const now = new Date();
            const curTime = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(curTime === alarm.time) {
                // 1. Ovoz chiqarib gapirish
                const msg = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi! Iltimos, doringizni iching.");
                msg.lang = 'uz-UZ';
                window.speechSynthesis.speak(msg);
                
                // 2. Bildirishnoma
                if(Notification.permission === 'granted') {
                    new Notification("⏰ VAQT BO'LDI!", { body: "Doringizni iching!" });
                }
                alert("⏰ DORI ICHISH VAQTI!!!");
            }
        }, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.json
    try:
        # AI ga qat'iy format beramiz
        prompt = f"Dori: {data['name']}. Til: {data['lang']}. Faqat 4 ta bandda qisqa yoz: Tarkibi:, Dozasi:, Foydasi:, Zarari:. Har birini yangi qatordan yoz."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except: return jsonify({"text": "AI bog'lanishda xato!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
