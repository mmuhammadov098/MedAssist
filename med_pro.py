import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
# GROQ_API_KEY ni Render settings'dan qo'shishni unutmang!
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 20px; }
        .main-card { background: white; width: 100%; max-width: 400px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; }
        .top-bar { background: #007bff; color: white; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; }
        .content { padding: 20px; }
        input, button { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }
        button { cursor: pointer; border: none; font-weight: bold; transition: 0.3s; }
        .btn-search { background: #007bff; color: white; }
        .btn-lang { width: 32%; display: inline-block; background: #6c757d; color: white; font-size: 12px; }
        .result-area { background: #fff; border: 1px solid #eee; padding: 15px; margin-top: 15px; min-height: 100px; border-left: 5px solid #007bff; }
        .alarm-area { margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 10px; border: 1px solid #ffeeba; }
        .blue-title { color: #007bff; font-weight: bold; margin-top: 10px; display: block; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="top-bar">💊 MedAssist Pro</div>
        <div class="content">
            <input type="text" id="drugInput" placeholder="Dori nomini yozing (masalan: Analgin)">
            
            <div style="display: flex; justify-content: space-between;">
                <button class="btn-lang" onclick="setLang('uz')">O'ZBEK</button>
                <button class="btn-lang" onclick="setLang('ru')">РУССКИЙ</button>
                <button class="btn-lang" onclick="setLang('en')">ENGLISH</button>
            </div>

            <button class="btn-search" onclick="searchDrug()">QIDIRISH</button>

            <div id="output" class="result-area">Ma'lumotlar bu yerda ko'rinadi...</div>

            <div class="alarm-area">
                <h4 style="margin: 0 0 10px 0; text-align: center;">⏰ ESLATMA O'RNATISH</h4>
                <input type="time" id="alarmTime">
                <button style="background: #28a745; color: white;" onclick="setupAlarm()">SAQLASH</button>
                <p id="alarmDisplay" style="text-align: center; color: #155724; font-size: 14px;"></p>
            </div>
        </div>
    </div>

    <script>
        let currentLang = 'uz';
        function setLang(l) { currentLang = l; alert("Til o'zgardi: " + l); }

        async function searchDrug() {
            const name = document.getElementById('drugInput').value;
            if(!name) return;
            const out = document.getElementById('output');
            out.innerHTML = "⌛ Qidirilmoqda...";

            try {
                const res = await fetch('/api/get', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, lang: currentLang})
                });
                const data = await res.json();
                
                // Ma'lumot chiqmaslik muammosini hal qilish:
                let text = data.text;
                let formatted = text.replace(/Tarkibi:/g, '<b class="blue-title">TARKIBI:</b>')
                                    .replace(/Dozasi:/g, '<b class="blue-title">DOZASI:</b>').replace(/Foydasi:/g, '<b class="blue-title">FOYDASI:</b>')
                                    .replace(/Zarari:/g, '<b class="blue-title">ZARARI:</b>');
                out.innerHTML = formatted;
            } catch (e) { out.innerHTML = "❌ Xato yuz berdi!"; }
        }

        function setupAlarm() {
            const t = document.getElementById('alarmTime').value;
            if(!t) return;
            localStorage.setItem('med_time', t);
            document.getElementById('alarmDisplay').innerText = "🔔 Eslatma " + t + " ga qo'yildi";
        }

        // Eslatmani tekshirish (Har 30 soniyada)
        setInterval(() => {
            const saved = localStorage.getItem('med_time');
            if(!saved) return;
            const d = new Date();
            const now = d.getHours().toString().padStart(2,'0') + ":" + d.getMinutes().toString().padStart(2,'0');
            
            if(now === saved) {
                alert("🚨 VAQT BO'LDI! DORINGIZNI ICHING! 🚨");
                localStorage.removeItem('med_time');
                document.getElementById('alarmDisplay').innerText = "";
            }
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/get', methods=['POST'])
def get_drug():
    data = request.json
    try:
        # AI ga aniq buyruq
        prompt = f"Dori: {data['name']}. Til: {data['lang']}. Faqat shu 4 ta punktda javob ber: Tarkibi:, Dozasi:, Foydasi:, Zarari:. Ortiqcha so'z yozma."
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": chat_completion.choices[0].message.content})
    except:
        return jsonify({"text": "Xato: AI bilan bog'lanib bo'lmadi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
