import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
# Render "Environment Variables" qismida GROQ_API_KEY borligiga ishonch hosil qiling
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
        body { background: #f0f2f5; padding: 15px; font-family: sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        #res { background: #fff; padding: 15px; border-radius: 12px; border: 1px solid #dee2e6; margin: 15px 0; min-height: 60px; font-size: 15px; }
        .alarm-section { background: #e8f5e9; padding: 20px; border-radius: 15px; border: 1px solid #c8e6c9; }
        .btn-success { background: #2e7d32; border: none; }
        .loading { color: #007bff; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist Pro</h3></div>
        <div class="p-4">
            <button onclick="enableNotif()" class="btn btn-outline-primary btn-sm w-100 mb-3">🔔 Xabarnomani yoqish</button>
            
            <input type="text" id="d" class="form-control mb-3" placeholder="Dori nomi...">
            <div class="d-flex gap-2">
                <button onclick="askAI('uz')" class="btn btn-primary w-100">O'zbekcha</button>
                <button onclick="askAI('ru')" class="btn btn-info text-white w-100">Русский</button>
            </div>

            <div id="res">Ma'lumot bu yerda chiqadi...</div>

            <div class="alarm-section mt-4">
                <h6 class="text-center fw-bold">⏰ Eslatma o'rnatish</h6>
                <div class="d-flex gap-2 my-3">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="saveAlarm()" class="btn btn-success w-100 py-2">Eslatmani saqlash</button>
                <div id="st" class="small mt-2 text-center text-success"></div>
            </div>
        </div>
    </div>

    <script>
        // Brauzer ruxsatini olish
        function enableNotif() {
            Notification.requestPermission().then(p => {
                if(p === 'granted') alert("Ruxsat berildi! Endi eslatma ishlaydi.");
            });
        }

        async function askAI(lang) {
            const name = document.getElementById('d').value;
            if(!name) return alert("Dori nomini yozing!");
            const resDiv = document.getElementById('res');
            resDiv.innerHTML = '<span class="loading">⌛ AI javob bermoqda, kuting...</span>';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, lang: lang})
                });
                const data = await response.json();
                resDiv.innerHTML = data.text.replace(/\\n/g, '<br>');
            } catch (e) {
                resDiv.innerHTML = "❌ Xatolik yuz berdi. Internetni yoki API kalitni tekshiring.";
            }
        }

        function saveAlarm() {
            const t = document.getElementById('v').value;
            const d = document.getElementById('k').value;
            if(!t || !d) return alert("Ma'lumotni to'liq kiriting!");const alarmData = { time: t, expire: Date.now() + (d * 86400000) };
            localStorage.setItem('med_alarm', JSON.stringify(alarmData));
            document.getElementById('st').innerText = "✅ Eslatma " + t + " ga o'rnatildi";
        }

        // Har 10 soniyada vaqtni tekshirish
        setInterval(() => {
            const alarm = JSON.parse(localStorage.getItem('med_alarm'));
            if(!alarm) return;
            
            const now = new Date();
            const curTime = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
            
            if(curTime === alarm.time) {
                // 1. Ovozli xabar (Faqat foydalanuvchi saytda bir marta bosgan bo'lsa ishlaydi)
                const speech = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                speech.lang = 'uz-UZ';
                window.speechSynthesis.speak(speech);
                
                // 2. Tepadagi xabarnoma
                if (Notification.permission === "granted") {
                    new Notification("⏰ MedAssist Pro", { body: "Dori ichish vaqti bo'ldi!", icon: "https://cdn-icons-png.flaticon.com/512/822/822143.png" });
                }
                
                // 3. Ekrandagi xabar
                alert("⏰ DORI ICHISH VAQTI BO'LDI!");
            }
        }, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    try:
        # Promptni maksimal soddalashtirdik
        prompt = f"Dori nomi: {data['name']}. Til: {data['lang']}. Tarkibi, dozasi, foydasi va zarari haqida qisqa va aniq ma'lumot ber."
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"text": f"Xato: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
