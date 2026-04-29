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
        .card { max-width: 550px; margin: auto; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: none; }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        .btn-l { width: 32%; font-weight: bold; border-radius: 10px; padding: 10px; }
        #res { background: white; padding: 20px; border-radius: 15px; margin-top: 15px; border: 1px solid #e0e0e0; min-height: 200px; }
        .section-title { color: #1a73e8; font-weight: bold; margin-top: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .content-text { margin-bottom: 15px; font-size: 15px; color: #333; }
        .loader { display: none; text-align: center; margin: 10px 0; font-weight: bold; color: #1a73e8; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <img src="https://img.icons8.com/color/96/pill.png" width="45" class="mb-2">
            <h4>MedAssist Pro</h4>
        </div>
        <div class="p-4 bg-white">
            <input type="text" id="inp" class="form-control mb-3 shadow-sm" placeholder="Dori nomini yozing (masalan: Paracetamol)...">
            <div class="d-flex justify-content-between mb-2">
                <button onclick="ask('uzbekcha')" class="btn btn-primary btn-l">O'zbek</button>
                <button onclick="ask('ruscha')" class="btn btn-info text-white btn-l">Русский</button>
                <button onclick="ask('inglizcha')" class="btn btn-dark btn-l">English</button>
            </div>
            <div class="loader" id="lod">🔍 Ma'lumot qidirilmoqda...</div>
            <div id="res">Dori haqida batafsil ma'lumot olish uchun tilni tanlang.</div>
            <div class="alert alert-warning mt-3 py-2 small text-center fw-bold">
                ⚠️ DIQQAT: SHIFOKOR MASLAHATI SHART!
            </div>
        </div>
    </div>
    <script>
        async function ask(til) {
            const d = document.getElementById('inp').value.trim();
            if(!d) return alert("Dori nomini yozing!");
            
            document.getElementById('lod').style.display = 'block';
            document.getElementById('res').innerHTML = "Yuklanmoqda...";

            try {
                const r = await fetch('/data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({n: d, l: til})
                });
                const data = await r.json();
                // HTML formatda chiqarish
                document.getElementById('res').innerHTML = data.t;
            } catch (e) {
                document.getElementById('res').innerText = "Xatolik yuz berdi.";
            } finally {
                document.getElementById('lod').style.display = 'none';
            }
        }
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
    
    # AI uchun juda aniq ko'rsatma (Structure Prompt)
    prompt = f"""
    Siz professional farmatsevtsiz. {dori} haqida ma'lumotni FAQAT {til} tilida bering.Javobni quyidagi HTML formatida bering (faqat div va b teglarini ishlating):
    
    <div class='section-title'>💊 Tarkibi:</div>
    <div class='content-text'>Dorining asosiy va yordamchi moddalari haqida qisqa ma'lumot.</div>
    
    <div class='section-title'>✨ Foydasi:</div>
    <div class='content-text'>Dori nima uchun va qanday kasalliklarda qo'llaniladi.</div>
    
    <div class='section-title'>📏 Dozasi va Qo'llash muddati:</div>
    <div class='content-text'>Kuniga necha mahal, qancha miqdorda va necha kun ichilishi haqida (kattalar va bolalar uchun alohida).</div>
    
    <div class='section-title'>🚫 Zarari va Nojo'ya ta'siri:</div>
    <div class='content-text'>Kimlarga mumkin emas va qanday zararli tomonlari bo'lishi mumkin.</div>
    
    Ma'lumotlar aniq va tibbiy asoslangan bo'lsin.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return jsonify({"t": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"t": f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
