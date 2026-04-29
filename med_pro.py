import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# API ulanishini tekshirish
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

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
        body { background: #f4f7f6; padding: 20px; font-family: sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none; }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        #res { background: white; padding: 15px; border-radius: 12px; border: 1px solid #ddd; margin-top: 15px; min-height: 50px; }
        .alarm-card { background: #e8f5e9; border: 1px solid #4caf50; padding: 15px; border-radius: 15px; margin-top: 15px; }
        .history-item { cursor: pointer; color: #1a73e8; font-weight: bold; padding: 5px 0; display: block; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h4>💊 MedAssist Pro</h4></div>
        <div class="p-4 bg-white">
            <input type="text" id="dori" class="form-control mb-3" placeholder="Dori nomini yozing...">
            <div class="d-flex justify-content-between mb-3 gap-1">
                <button onclick="ask('uzbekcha')" class="btn btn-primary w-100">O'zbek</button>
                <button onclick="ask('ruscha')" class="btn btn-info text-white w-100">Русский</button>
                <button onclick="ask('inglizcha')" class="btn btn-dark w-100">English</button>
            </div>
            
            <div id="res">Natija kutilyapti...</div>

            <div class="alarm-card">
                <h6 class="text-center">⏰ Kursli Eslatma</h6>
                <div class="d-flex gap-2 mb-2">
                    <input type="time" id="vqt" class="form-control">
                    <input type="number" id="kun" class="form-control" placeholder="Kun">
                </div>
                <button onclick="setAlarm()" class="btn btn-success btn-sm w-100 fw-bold">Eslatmani Faollashtirish</button>
                <div id="status" class="small mt-2 text-success text-center font-weight-bold"></div>
            </div>

            <div class="mt-3">
                <h6>📜 Tarix:</h6>
                <div id="hist" class="small"></div>
            </div>
        </div>
    </div>

    <script>
        async function ask(til) {
            const dori = document.getElementById('dori').value.trim();
            if(!dori) return alert("Dori nomini kiriting!");
            
            const resDiv = document.getElementById('res');
            resDiv.innerHTML = "⌛ Yuklanmoqda, iltimos kuting...";
            
            try {
                const response = await fetch('/data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({n: dori, l: til})
                });
                const data = await response.json();
                resDiv.innerHTML = data.t;
                saveHistory(dori);
            } catch (error) {
                resDiv.innerHTML = "⚠️ Server bilan bog'lanib bo'lmadi. Sahifani yangilab ko'ring.";
            }
        }

        function setAlarm() {
            const time = document.getElementById('vqt').value;
            const days = document.getElementById('kun').value;if(!time || !days) return alert("Vaqt va kunni to'liq kiriting!");
            
            const endDate = new Date();
            endDate.setDate(endDate.getDate() + parseInt(days));
            
            localStorage.setItem('med_alarm', JSON.stringify({t: time, e: endDate.getTime()}));
            document.getElementById('status').innerText = ✅ ${days} kunlik eslatma ${time} ga qo'yildi.;
        }

        setInterval(() => {
            const alarm = JSON.parse(localStorage.getItem('med_alarm'));
            if(!alarm) return;
            
            const now = new Date();
            if(now.getTime() > alarm.e) {
                localStorage.removeItem('med_alarm');
                return;
            }
            
            const currentStr = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            if(currentStr === alarm.t) {
                // Brauzer ovozli ogohlantirishi
                const utter = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                window.speechSynthesis.speak(utter);
                alert("⏰ VAQT BO'LDI! Doriningizni iching.");
            }
        }, 30000);

        function saveHistory(n) {
            let h = JSON.parse(localStorage.getItem('med_h') || '[]');
            if(!h.includes(n)) { h.unshift(n); if(h.length>5) h.pop(); localStorage.setItem('med_h', JSON.stringify(h)); }
            updateHistoryUI();
        }
        function updateHistoryUI() {
            let h = JSON.parse(localStorage.getItem('med_h') || '[]');
            document.getElementById('hist').innerHTML = h.map(i => <span class="history-item" onclick="document.getElementById('dori').value='${i}'">${i}</span>).join('');
        }
        updateHistoryUI();
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
    dori_nomi = req.get('n')
    til = req.get('l')
    
    if not client:
        return jsonify({"t": "API Kalit o'rnatilmagan. Render sozlamalarini tekshiring."})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{dori_nomi} haqida {til} tilida tarkibi, foydasi, dozasi va zarari haqida qisqa HTML formatda ma'lumot ber."}]
        )
        return jsonify({"t": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"t": f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
