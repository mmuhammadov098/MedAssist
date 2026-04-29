import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# API Kalitni tekshirish
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding: 15px; font-family: sans-serif; }
        .card { max-width: 450px; margin: auto; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: none; }
        .header { background: #1a73e8; color: white; padding: 15px; text-align: center; border-radius: 15px 15px 0 0; }
        #res { background: #fff; padding: 12px; border-radius: 10px; border: 1px solid #eee; margin: 15px 0; font-size: 15px; }
        .alarm-box { background: #fff3cd; padding: 15px; border-radius: 12px; border: 1px solid #ffeeba; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h5>💊 MedAssist AI</h5></div>
        <div class="p-3 bg-white">
            <input type="text" id="d" class="form-control mb-2" placeholder="Dori nomi...">
            <button onclick="ask()" class="btn btn-primary w-100 mb-3">Qidirish</button>
            
            <div id="res">Natija kutilyapti...</div>

            <div class="alarm-box">
                <h6 class="text-center fw-bold">⏰ Eslatma</h6>
                <div class="d-flex gap-2 mb-2">
                    <input type="time" id="v" class="form-control">
                    <input type="number" id="k" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setA()" class="btn btn-warning w-100 fw-bold">Yoqish</button>
                <div id="st" class="small mt-2 text-center text-success"></div>
            </div>
        </div>
    </div>

    <script>
        async function ask() {
            const n = document.getElementById('d').value;
            if(!n) return alert("Dori nomini yozing!");
            document.getElementById('res').innerHTML = "⌛ Yuklanmoqda...";
            try {
                const r = await fetch('/data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({n: n})
                });
                const data = await r.json();
                document.getElementById('res').innerHTML = data.t;
            } catch { document.getElementById('res').innerHTML = "⚠️ Xatolik! Sahifani yangilang."; }
        }

        function setA() {
            const v = document.getElementById('v').value;
            const k = document.getElementById('k').value;
            if(!v || !k) return alert("To'liq to'ldiring!");
            const e = new Date().getTime() + (k * 86400000);
            localStorage.setItem('al', JSON.stringify({v:v, e:e}));
            document.getElementById('st').innerText = "✅ Eslatma qo'yildi: " + v;
            alert("Eslatma yoqildi!");
        }

        setInterval(() => {
            const a = JSON.parse(localStorage.getItem('al'));
            if(!a) return;
            const n = new Date();
            const c = n.getHours().toString().padStart(2,'0') + ":" + n.getMinutes().toString().padStart(2,'0');
            if(c === a.v) {
                const s = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                window.speechSynthesis.speak(s);
                alert("⏰ VAQT BO'LDI! Dori iching.");
            }
        }, 15000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)@app.route('/data', methods=['POST'])
def data():
    req = request.json
    if not client: return jsonify({"t": "API Kalit topilmadi!"})
    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{req['n']} dorisi haqida tarkibi, dozasi va zarari haqida judayam qisqa (max 3-4 qator) ma'lumot ber. Tarixi kerak emas."}]
        )
        return jsonify({"t": chat.choices[0].message.content})
    except Exception as e:
        return jsonify({"t": "Serverda xatolik yuz berdi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
