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
        body { background: linear-gradient(180deg, #f0f4f8 0%, #d9e2ec 100%); min-height: 100vh; padding: 15px; font-family: sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: none; background: white; overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .lang-btn { flex: 1; border-radius: 12px; font-weight: bold; padding: 10px; border: none; }
        
        /* Ma'lumotlarni chiroyli chiqarish */
        .res-item { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #f1f5f9; }
        .res-title { color: #007bff; font-weight: bold; display: block; font-size: 14px; text-transform: uppercase; }
        .res-content { color: #334155; font-size: 15px; display: block; margin-top: 2px; }
        
        #res { background: #fff; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; margin: 15px 0; min-height: 50px; }
        .alarm-section { background: #fffbeb; padding: 20px; border-radius: 20px; border: 1px solid #fef3c7; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist Pro</h3></div>
        <div class="p-4">
            <button onclick="reqPermission()" id="pBtn" class="btn btn-outline-primary btn-sm w-100 mb-3">🔔 Bildirishnomaga ruxsat berish</button>
            
            <input type="text" id="d" class="form-control mb-3" placeholder="Dori nomi...">
            <div class="d-flex gap-2 mb-3">
                <button onclick="ask('uz')" class="btn btn-primary lang-btn">O'zbek</button>
                <button onclick="ask('ru')" class="btn btn-info text-white lang-btn">Русский</button>
                <button onclick="ask('en')" class="btn btn-dark lang-btn">English</button>
            </div>

            <div id="res">Natija kutilmoqda...</div>

            <div class="alarm-section mt-4">
                <h6 class="text-center fw-bold mb-3">⏰ Dori ichish eslatmasi</h6>
                <div class="d-flex gap-2 mb-3">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-warning w-100 fw-bold shadow-sm">Eslatmani yoqish</button>
                <div id="st" class="small mt-2 text-center text-success fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        function reqPermission() {
            Notification.requestPermission().then(perm => {
                if(perm === 'granted') {
                    alert("Ruxsat berildi! Endi xabar keladi.");
                    document.getElementById('pBtn').style.display = 'none';
                }
            });
        }

        async function ask(lang) {
            const name = document.getElementById('d').value;
            if(!name) return alert("Dori nomini yozing!");
            const resDiv = document.getElementById('res');
            resDiv.innerHTML = "⌛ AI o'ylamoqda...";
            
            try {
                const response = await fetch('/get_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, lang: lang})});
                const data = await response.json();
                
                // Matnni chiroyli qismlarga ajratamiz
                let lines = data.text.split('\\n').filter(l => l.trim() !== "");
                let finalHtml = "";
                lines.forEach(line => {
                    if(line.includes(':')) {
                        let [title, ...content] = line.split(':');
                        finalHtml += <div class="res-item"><span class="res-title">${title.trim()}:</span><span class="res-content">${content.join(':').trim()}</span></div>;
                    } else {
                        finalHtml += <div class="res-item"><span class="res-content">${line}</span></div>;
                    }
                });
                resDiv.innerHTML = finalHtml;
            } catch { resDiv.innerHTML = "⚠️ Xato yuz berdi."; }
        }

        function setAlarm() {
            const time = document.getElementById('v').value;
            const days = document.getElementById('k').value;
            if(!time || !days) return alert("To'ldiring!");
            
            const expire = new Date().getTime() + (days * 86400000);
            localStorage.setItem('med_alarm', JSON.stringify({time: time, expire: expire}));
            document.getElementById('st').innerText = "✅ " + time + " ga qo'yildi";
            alert("Eslatildi!");
        }

        setInterval(() => {
            const alarm = JSON.parse(localStorage.getItem('med_alarm'));
            if(!alarm) return;
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(cur === alarm.time) {
                // Ovozli xabar
                const speech = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                speech.lang = 'uz-UZ';
                window.speechSynthesis.speak(speech);
                
                // Tepadagi bildirishnoma
                if (Notification.permission === "granted") {
                    new Notification("⏰ MedAssist: Dori vaqti!", { body: "Iltimos, doringizni iching." });
                }
                alert("⏰ Dori vaqti bo'ldi!");
            }
        }, 30000);
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
        # Promptni aniqlashtiramiz
        prompt = f"Dori: {data['name']}. Til: {data['lang']}. Faqat quyidagilarni yoz: Tarkibi, Dozasi, Foydasi, Zarari. Har birini yangi qatorda sarlavha bilan yoz (masalan, Tarkibi: ...)."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except: return jsonify({"text": "AI xatosi!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
