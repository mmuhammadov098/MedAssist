import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# API ulanishi
GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

HTML_PAGE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 20px; font-family: sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        #res { background: white; padding: 15px; border-radius: 12px; border: 1px solid #ddd; margin: 15px 0; min-height: 50px; font-size: 14px; }
        .alarm { background: #fff3cd; padding: 15px; border-radius: 15px; border: 1px solid #ffeeba; }
    </style>
</head>
<body>
    <div class="card p-4">
        <h4 class="text-center text-primary mb-4">💊 MedAssist AI</h4>
        <input type="text" id="dori" class="form-control mb-2" placeholder="Dori nomi...">
        <button onclick="search()" class="btn btn-primary w-100 mb-3">Ma'lumot olish</button>
        
        <div id="res">Natija kutilyapti...</div>

        <div class="alarm">
            <h6 class="text-center fw-bold">⏰ Eslatma o'rnatish</h6>
            <div class="d-flex gap-2 mb-2">
                <input type="time" id="vqt" class="form-control">
                <input type="number" id="kun" class="form-control" placeholder="Kun">
            </div>
            <button onclick="setAl()" class="btn btn-warning w-100 fw-bold">Eslatmani yoqish</button>
            <div id="st" class="small mt-2 text-center text-success fw-bold"></div>
        </div>
    </div>

    <script>
        async function search() {
            const n = document.getElementById('dori').value;
            if(!n) return alert("Nomini yozing!");
            document.getElementById('res').innerHTML = "⌛ AI qidirmoqda...";
            
            try {
                const r = await fetch('/get_data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: n})
                });
                const data = await r.json();
                document.getElementById('res').innerHTML = data.text;
            } catch (e) {
                document.getElementById('res').innerHTML = "⚠️ Xato! Serverda muammo.";
            }
        }

        function setAl() {
            const v = document.getElementById('vqt').value;
            const k = document.getElementById('kun').value;
            if(!v || !k) return alert("To'ldiring!");
            const endTime = new Date().getTime() + (k * 86400000);
            localStorage.setItem('med_a', JSON.stringify({v: v, e: endTime}));
            document.getElementById('st').innerText = "🔔 " + v + " ga qo'yildi";
            alert("Eslatma faol!");
        }

        setInterval(() => {
            const a = JSON.parse(localStorage.getItem('med_a'));
            if(!a) return;
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            if(cur === a.v) {
                const s = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                window.speechSynthesis.speak(s);
                alert("⏰ VAQT BO'LDI!");
            }
        }, 15000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/get_data', methods=['POST'])
def get_data():req = request.json
    if not client: return jsonify({"text": "API Kalit xato!"})
    try:
        # Promptni maksimal qisqartirdik
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{req['name']} dorisi tarkibi va dozasi haqida faqat 3 qatorda yoz. Ortiqcha gap kerakmas."}]
        )
        return jsonify({"text": res.choices[0].message.content})
    except Exception as e:
        return jsonify({"text": f"Xato: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
