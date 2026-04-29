import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
# Render'da GROQ_API_KEY o'zgaruvchisini sozlashni unutmang
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
        body { background: #f4f7f6; padding: 20px; font-family: sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none; }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        .btn-l { width: 32%; font-weight: bold; border-radius: 10px; }
        #res { background: white; padding: 15px; border-radius: 10px; min-height: 150px; margin-top: 15px; border: 1px solid #eee; white-space: pre-wrap; line-height: 1.6; }
        .loader { display: none; text-align: center; margin-top: 10px; }
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
            <div class="d-flex justify-content-between">
                <button onclick="ask('uzbekcha')" class="btn btn-primary btn-l">O'zbek</button>
                <button onclick="ask('ruscha')" class="btn btn-info text-white btn-l">Русский</button>
                <button onclick="ask('inglizcha')" class="btn btn-dark btn-l">English</button>
            </div>
            <div class="loader" id="lod">Qidirilmoqda...</div>
            <div id="res">Dori ma'lumoti bu yerda chiqadi.</div>
            <p class="text-danger mt-3 small text-center fw-bold">⚠️ SHIFOKOR MASLAHATI SHART!</p>
        </div>
    </div>
    <script>
        async function ask(til) {
            const d = document.getElementById('inp').value.trim();
            if(!d) return alert("Dori nomini yozing!");
            
            document.getElementById('lod').style.display = 'block';
            document.getElementById('res').innerText = "";

            try {
                const r = await fetch('/data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({n: d, l: til})
                });
                const data = await r.json();
                document.getElementById('res').innerText = data.t;
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
    
    prompt = f"Siz professional farmatsevtsiz. {dori} haqida tarkibi, dozasi va foydasi haqida FAQAT {til} tilida batafsil ma'lumot bering. To'qib chiqarmang."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return jsonify({"t": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"t": f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
