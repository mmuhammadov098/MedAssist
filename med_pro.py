import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# GROQ API sozlamasi
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Sahifa ko'rinishi
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link rel="icon" href="https://img.icons8.com/color/96/pill.png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 20px; font-family: sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        #res { background: white; padding: 15px; border-radius: 12px; border: 1px solid #ddd; margin-top: 15px; }
        .alarm-card { background: #e8f5e9; border: 1px solid #4caf50; padding: 15px; border-radius: 15px; margin-top: 15px; }
        .history-item { cursor: pointer; color: #1a73e8; padding: 5px 0; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h4>💊 MedAssist Pro</h4></div>
        <div class="p-4 bg-white">
            <input type="text" id="dori" class="form-control mb-3" placeholder="Dori nomini yozing...">
            <div class="d-flex justify-content-between mb-3">
                <button onclick="ask('uzbekcha')" class="btn btn-primary w-100 me-1">O'zbek</button>
                <button onclick="ask('ruscha')" class="btn btn-info text-white w-100 me-1">Русский</button>
                <button onclick="ask('inglizcha')" class="btn btn-dark w-100">English</button>
            </div>
            
            <div id="res">Natija...</div>

            <div class="alarm-card text-center">
                <h6>⏰ Kursli Eslatma</h6>
                <div class="d-flex gap-2 mb-2">
                    <input type="time" id="vqt" class="form-control">
                    <input type="number" id="kun" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-success btn-sm w-100 fw-bold">Eslatmani Yoqish</button>
                <div id="status" class="small mt-2 text-success"></div>
            </div>

            <div class="mt-3">
                <h6>📜 Tarix:</h6>
                <div id="hist" class="small"></div>
            </div>
        </div>
    </div>

    <script>
        async function ask(t) {
            const n = document.getElementById('dori').value;
            if(!n) return alert("Dori nomini yozing");
            document.getElementById('res').innerHTML = "Yuklanmoqda...";
            
            const r = await fetch('/data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n: n, l: t})
            });
            const data = await r.json();
            document.getElementById('res').innerHTML = data.t;
            save(n);
        }

        function setAlarm() {
            const v = document.getElementById('vqt').value;
            const k = document.getElementById('kun').value;
            if(!v || !k) return alert("Vaqt va kunni kiriting!");
            
            const end = new Date();
            end.setDate(end.getDate() + parseInt(k));
            localStorage.setItem('med_alarm', JSON.stringify({t: v, e: end.getTime()}));
            document.getElementById('status').innerText = k + " kunlik eslatma yoqildi: " + v;
        }

        setInterval(() => {
            const a = JSON.parse(localStorage.getItem('med_alarm'));if(!a) return;
            if(new Date().getTime() > a.e) return localStorage.removeItem('med_alarm');
            
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            if(cur === a.t) {
                window.speechSynthesis.speak(new SpeechSynthesisUtterance("Dori vaqti bo'ldi!"));
                alert("⏰ VAQT BO'LDI!");
            }
        }, 40000);

        function save(n) {
            let h = JSON.parse(localStorage.getItem('h') || '[]');
            if(!h.includes(n)) { h.unshift(n); if(h.length>5) h.pop(); localStorage.setItem('h', JSON.stringify(h)); }
            showH();
        }
        function showH() {
            let h = JSON.parse(localStorage.getItem('h') || '[]');
            document.getElementById('hist').innerHTML = h.map(i => <div class="history-item" onclick="document.getElementById('dori').value='${i}'">${i}</div>).join('');
        }
        showH();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/data', methods=['POST'])
def data():
    req = request.json
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{req['n']} haqida {req['l']} tilida tarkibi, foydasi, dozasi va zarari haqida HTML formatda ma'lumot ber."}]
        )
        return jsonify({"t": res.choices[0].message.content})
    except:
        return jsonify({"t": "Xatolik yuz berdi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
