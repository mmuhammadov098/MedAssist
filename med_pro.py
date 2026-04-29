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
        #res { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; min-height: 150px; margin-top: 15px; }
        .alarm-card { background: #e8f5e9; padding: 15px; border-radius: 15px; margin-top: 20px; border: 1px solid #4caf50; }
        .history-item { cursor: pointer; padding: 8px; border-bottom: 1px solid #eee; color: #1a73e8; }
        .section-title { color: #1a73e8; font-weight: bold; margin-top: 10px; }
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
            
            <div id="res">Natija bu yerda chiqadi.</div>

            <div class="alarm-card">
                <h6>⏰ Kursli eslatma o'rnatish:</h6>
                <div class="row g-2">
                    <div class="col-6">
                        <label class="small">Vaqti:</label>
                        <input type="time" id="alarmTime" class="form-control">
                    </div>
                    <div class="col-6">
                        <label class="small">Kunlar soni:</label>
                        <input type="number" id="alarmDays" class="form-control" placeholder="Masalan: 3" min="1">
                    </div>
                </div>
                <button onclick="setSmartAlarm()" class="btn btn-success btn-sm w-100 mt-2 fw-bold">Eslatmani yoqish</button>
                <div id="alarmStatus" class="small mt-2 text-success fw-bold text-center"></div>
            </div>

            <div class="mt-4">
                <h6>📜 Oxirgi qidiruvlar:</h6>
                <div id="historyList" class="small"></div>
            </div>
        </div>
    </div>

    <script>
        async function ask(til) {
            const d = document.getElementById('inp').value.trim();
            if(!d) return alert("Dori nomini yozing!");
            document.getElementById('res').innerHTML = "Yuklanmoqda...";
            
            const r = await fetch('/data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n: d, l: til})
            });
            const data = await r.json();
            document.getElementById('res').innerHTML = data.t;
            addToHistory(d);
        }function addToHistory(name) {
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
            document.getElementById('historyList').innerHTML = history.map(item => <div class="history-item" onclick="document.getElementById('inp').value='${item}'">${item}</div>).join('');
        }

        // AQLLI BUDILNIK FUNKSIYASI
        function setSmartAlarm() {
            const time = document.getElementById('alarmTime').value;
            const days = parseInt(document.getElementById('alarmDays').value);

            if(!time || !days) return alert("Vaqt va kunni to'liq kiriting!");

            const startDate = new Date();
            const endDate = new Date();
            endDate.setDate(startDate.getDate() + days);

            const alarmConfig = {
                time: time,
                endTimestamp: endDate.getTime(),
                daysLeft: days
            };

            localStorage.setItem('smartAlarm', JSON.stringify(alarmConfig));
            document.getElementById('alarmStatus').innerText = ✅ ${days} kunlik eslatma ${time} ga qo'yildi!;
            alert(${days} kun davomida har kuni soat ${time}da eslatma beriladi.);
        }

        setInterval(() => {
            const alarmData = JSON.parse(localStorage.getItem('smartAlarm'));
            if(!alarmData) return;

            const now = new Date();
            const currentTimestamp = now.getTime();

            // Muddat tugaganini tekshirish
            if(currentTimestamp > alarmData.endTimestamp) {
                localStorage.removeItem('smartAlarm');
                document.getElementById('alarmStatus').innerText = "🏁 Kurs yakunlandi.";
                return;
            }

            const currentTimeStr = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
            
            if(currentTimeStr === alarmData.time) {
                // Ovozli xabar
                const msg = new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!");
                window.speechSynthesis.speak(msg);
                
                alert("⏰ VAQT BO'LDI! Doriningizni iching.");
                // Bir minut davomida qayta-qayta chiqmasligi uchun biroz kutish
            }
        }, 30000); // Har 30 soniyada tekshiradi

        updateHistoryUI();
    </script>
</body>
</html>
"""

@app.route('/data', methods=['POST'])
def data():
    req = request.json
    prompt = f"Professional farmatsevtsiz. {req.get('n')} haqida tarkibi, foydasi, dozasi va zarari haqida {req.get('l')} tilida HTML formatda ma'lumot bering."
    try:
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        return jsonify({"t": completion.choices[0].message.content})
    except:
        return jsonify({"t": "Xatolik."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
