import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link rel="icon" href="https://img.icons8.com/color/96/pill.png" type="image/png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .card { max-width: 550px; margin: auto; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: none; margin-bottom: 20px; }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        .btn-l { width: 32%; font-weight: bold; border-radius: 10px; }
        #res { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; min-height: 150px; }
        .section-title { color: #1a73e8; font-weight: bold; margin-top: 10px; border-bottom: 1px solid #eee; }
        .content-text { margin-bottom: 15px; font-size: 15px; }
        .history-item { cursor: pointer; padding: 8px; border-bottom: 1px solid #eee; color: #1a73e8; }
        .history-item:hover { background: #f8f9fa; }
        .alarm-card { background: #e3f2fd; padding: 15px; border-radius: 15px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <img src="https://img.icons8.com/color/96/pill.png" width="45" class="mb-2">
            <h4>MedAssist Pro</h4>
        </div>
        <div class="p-4 bg-white">
            <input type="text" id="inp" class="form-control mb-3" placeholder="Dori nomini yozing...">
            <div class="d-flex justify-content-between mb-3">
                <button onclick="ask('uzbekcha')" class="btn btn-primary btn-l">O'zbek</button>
                <button onclick="ask('ruscha')" class="btn btn-info text-white btn-l">Русский</button>
                <button onclick="ask('inglizcha')" class="btn btn-dark btn-l">English</button>
            </div>
            
            <div id="res">Natija...</div>

            <div class="alarm-card">
                <h6>⏰ Dori ichish eslatmasi:</h6>
                <div class="d-flex gap-2">
                    <input type="time" id="alarmTime" class="form-control">
                    <button onclick="setAlarm()" class="btn btn-success btn-sm">O'rnatish</button>
                </div>
                <div id="alarmStatus" class="small mt-2 text-muted"></div>
            </div>

            <div class="mt-4">
                <h6>📜 Oxirgi qidiruvlar:</h6>
                <div id="historyList" class="small"></div>
                <button onclick="clearHistory()" class="btn btn-link btn-sm p-0 text-danger">Tarixni tozalash</button>
            </div>
        </div>
    </div>

    <script>
        // 1. Qidiruv tarixini yuklash
        document.addEventListener('DOMContentLoaded', updateHistoryUI);

        async function ask(til) {
            const d = document.getElementById('inp').value.trim();
            if(!d) return alert("Dori nomini yozing!");
            
            document.getElementById('res').innerHTML = "Yuklanmoqda...";
            addToHistory(d);

            const r = await fetch('/data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n: d, l: til})
            });
            const data = await r.json();
            document.getElementById('res').innerHTML = data.t;
        }

        // Qidiruv tarixi funksiyalarifunction addToHistory(name) {
            let history = JSON.parse(localStorage.getItem('medHistory') || '[]');
            if(!history.includes(name)) {
                history.unshift(name);
                if(history.length > 5) history.pop();
                localStorage.setItem('medHistory', JSON.stringify(history));
                updateHistoryUI();
            }
        }

        function updateHistoryUI() {
            let history = JSON.parse(localStorage.getItem('medHistory') || '[]');
            const list = document.getElementById('historyList');
            list.innerHTML = history.map(item => <div class="history-item" onclick="document.getElementById('inp').value='${item}'">${item}</div>).join('');
        }

        function clearHistory() {
            localStorage.removeItem('medHistory');
            updateHistoryUI();
        }

        // 2. Budilnik funksiyasi
        function setAlarm() {
            const time = document.getElementById('alarmTime').value;
            if(!time) return alert("Vaqtni tanlang!");
            localStorage.setItem('medAlarm', time);
            document.getElementById('alarmStatus').innerText = "Eslatma o'rnatildi: " + time;
            checkAlarm();
        }

        function checkAlarm() {
            setInterval(() => {
                const now = new Date();
                const currentTime = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
                const savedTime = localStorage.getItem('medAlarm');
                
                if(currentTime === savedTime) {
                    alert("⏰ VAQT BO'LDI! Doriningizni ichishni unutmang!");
                    localStorage.removeItem('medAlarm'); // Bir marta chalingandan keyin o'chirish
                    document.getElementById('alarmStatus').innerText = "";
                }
            }, 1000 * 30); // Har 30 soniyada tekshirish
        }
        checkAlarm();
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
    dori = req.get('n')
    til = req.get('l')
    prompt = f"Siz professional farmatsevtsiz. {dori} haqida tarkibi, foydasi, dozasi va zarari haqida FAQAT {til} tilida HTML formatda (div va b teglari bilan) ma'lumot bering."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"t": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"t": "Xatolik yuz berdi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
