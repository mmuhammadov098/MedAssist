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
    <title>MedAssist Pro AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* 2-rasmdagi gradient fon */
        body { background: linear-gradient(180deg, #f0f4f8 0%, #d9e2ec 100%); min-height: 100vh; padding: 15px; font-family: sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: none; overflow: hidden; background: white; }
        .header { background: #007bff; color: white; padding: 25px; text-align: center; }
        .lang-btn { flex: 1; border-radius: 12px; font-weight: bold; padding: 12px; border: none; transition: 0.3s; }
        
        /* Ma'lumotlarni ko'k yozuvda ajratish */
        .info-title { color: #007bff; font-weight: bold; margin-top: 10px; display: block; text-transform: uppercase; font-size: 13px; }
        .info-text { display: block; margin-bottom: 10px; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 5px; }
        
        #res { background: #fff; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; margin: 15px 0; }
        .alarm-section { background: #fffbeb; padding: 20px; border-radius: 15px; border: 1px solid #fef3c7; }
        .btn-warning { background: #fbbf24; border: none; color: #92400e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist Pro</h3></div>
        <div class="p-4">
            <button onclick="requestNotif()" class="btn btn-outline-primary btn-sm w-100 mb-3">🔔 Bildirishnomaga ruxsat berish</button>
            
            <input type="text" id="d" class="form-control mb-3 py-2" placeholder="Dori nomi...">
            
            <div class="d-flex gap-2 mb-3">
                <button onclick="ask('uz')" class="btn btn-primary lang-btn">O'zbek</button>
                <button onclick="ask('ru')" class="btn btn-info text-white lang-btn">Русский</button>
                <button onclick="ask('en')" class="btn btn-dark lang-btn">English</button>
            </div>

            <div id="res">Ma'lumotlar...</div>

            <div class="alarm-section mt-4">
                <h6 class="text-center mb-3">⏰ Dori ichish eslatmasi</h6>
                <div class="d-flex gap-2 mb-3">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-warning w-100 py-2">Eslatmani yoqish</button>
                <div id="st" class="small mt-2 text-center text-success fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        // Bildirishnoma uchun ruxsat so'rash
        function requestNotif() {
            Notification.requestPermission().then(p => {
                if(p === 'granted') alert("Ruxsat berildi! Endi tepadab xabar keladi.");
            });
        }

        async function ask(lang) {
            const name = document.getElementById('d').value;
            if(!name) return;
            document.getElementById('res').innerHTML = "⌛...";
            
            try {
                const response = await fetch('/get_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, lang: lang})
                });const data = await response.json();
                
                // Ko'k yozuvda ajratib chiqarish
                let html = "";
                const parts = data.text.split('\\n');
                parts.forEach(p => {
                    if(p.includes(':')) {
                        let [title, text] = p.split(':');
                        html += <span class="info-title">${title}:</span><span class="info-text">${text}</span>;
                    }
                });
                document.getElementById('res').innerHTML = html || data.text;
            } catch { document.getElementById('res').innerHTML = "Xato!"; }
        }

        function setAlarm() {
            const time = document.getElementById('v').value;
            const days = document.getElementById('k').value;
            if(!time || !days) return;
            
            const expire = new Date().getTime() + (days * 86400000);
            localStorage.setItem('med_alarm', JSON.stringify({time: time, expire: expire}));
            document.getElementById('st').innerText = "✅ " + time + " ga qo'yildi";
        }

        setInterval(() => {
            const alarm = JSON.parse(localStorage.getItem('med_alarm'));
            if(!alarm) return;
            
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(cur === alarm.time) {
                // 1. Ovozli xabar (Gapirish)
                const speech = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi! Iltimos doringizni iching.");
                speech.lang = 'uz-UZ';
                window.speechSynthesis.speak(speech);
                
                // 2. Tepadagi Bildirishnoma (Push)
                if (Notification.permission === "granted") {
                    new Notification("⏰ Dori vaqti bo'ldi!", {
                        body: "Iltimos, doringizni ichishni unutmang.",
                        icon: "https://cdn-icons-png.flaticon.com/512/883/883356.png"
                    });
                }
                
                alert("⏰ VAQT BO'LDI!");
            }
        }, 20000);
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
        # Prompt: Ma'lumotlarni sarlavha bilan qaytarishini so'raymiz
        prompt = f"{data['name']} dorisi haqida {data['lang']} tilda faqat: Tarkibi, Dozasi, Foydasi va Zarari haqida yoz. Har birini yangi qatorda sarlavha bilan yoz."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except: return jsonify({"text": "Xato!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
