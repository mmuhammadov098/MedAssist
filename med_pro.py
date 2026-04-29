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
        body { background: #f8fafc; padding: 15px; font-family: 'Segoe UI', system-ui, sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none; overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .lang-btn { flex: 1; border-radius: 12px; font-weight: 600; padding: 10px; transition: 0.3s; }
        #res { background: #fff; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; margin: 15px 0; min-height: 100px; font-size: 15px; line-height: 1.6; color: #334155; }
        .alarm-section { background: #fffbeb; padding: 20px; border-radius: 15px; border: 1px solid #fef3c7; }
        .btn-warning { background: #fbbf24; border: none; color: #92400e; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h3>💊 MedAssist AI</h3></div>
        <div class="p-4 bg-white">
            <input type="text" id="d" class="form-control mb-3 py-2" placeholder="Dori nomini yozing...">
            
            <div class="d-flex gap-2 mb-3">
                <button onclick="ask('uz')" class="btn btn-primary lang-btn">O'zbek</button>
                <button onclick="ask('ru')" class="btn btn-info text-white lang-btn">Русский</button>
                <button onclick="ask('en')" class="btn btn-dark lang-btn">English</button>
            </div>

            <div id="res">Qidiruv natijasi bu yerda chiqadi...</div>

            <div class="alarm-section mt-4">
                <h6 class="text-center fw-bold mb-3">⏰ Dori ichish eslatmasi</h6>
                <div class="d-flex gap-2 mb-3">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-warning w-100 fw-bold py-2 shadow-sm">Eslatmani yoqish</button>
                <div id="st" class="small mt-2 text-center text-success fw-bold"></div>
            </div>
        </div>
    </div>

    <script>
        async function ask(lang) {
            const name = document.getElementById('d').value;
            if(!name) return alert("Iltimos, dori nomini kiriting!");
            
            const resDiv = document.getElementById('res');
            resDiv.innerHTML = "⌛ AI ma'lumot tayyorlamoqda...";
            
            try {
                const response = await fetch('/get_med_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, lang: lang})
                });
                const data = await response.json();
                resDiv.innerHTML = data.text;
            } catch {
                resDiv.innerHTML = "⚠️ Xatolik yuz berdi. Serverni tekshiring.";
            }
        }

        function setAlarm() {
            const time = document.getElementById('v').value;
            const days = document.getElementById('k').value;
            if(!time || !days) return alert("Vaqt va kunni to'liq to'ldiring!");
            
            const expire = new Date().getTime() + (days * 86400000);
            localStorage.setItem('med_reminder', JSON.stringify({time: time, expire: expire}));
            document.getElementById('st').innerText = "✅ Eslatma " + time + " ga qo'yildi";
            alert("Eslatma faollashtirildi!");
        }setInterval(() => {
            const reminder = JSON.parse(localStorage.getItem('med_reminder'));
            if(!reminder) return;
            
            const now = new Date();
            const currentTime = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(currentTime === reminder.time) {
                // Ovozli xabar berish
                const speech = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                speech.lang = 'uz-UZ';
                window.speechSynthesis.speak(speech);
                
                // Ekranda ogohlantirish
                alert("⏰ VAQT BO'LDI! Iltimos, doringizni iching.");
            }
        }, 15000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/get_med_info', methods=['POST'])
def get_med_info():
    data = request.json
    name = data.get('name')
    lang = data.get('lang')
    
    l_map = {'uz': "o'zbek tilida", 'ru': 'на русском языке', 'en': 'in English'}
    target_lang = l_map.get(lang, "o'zbek tilida")
    
    try:
        # AI uchun aniq ko'rsatma: faqat tarkibi, dozasi, foydasi va zarari
        prompt = f"Dori nomi: {name}. Ushbu dori haqida {target_lang} faqat quyidagi tartibda ma'lumot ber: 1. Tarkibi, 2. Dozasi, 3. Foydasi, 4. Zarari (nojo'ya ta'siri). Ma'lumot juda qisqa, aniq va jami 5-6 qatordan oshmasin. Tarixi yoki boshqa ortiqcha gap yozma."
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"text": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"text": "AI bilan bog'lanishda xato!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
