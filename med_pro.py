import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Diqqat: Bu yerda bitta qo'shtirnoq ham xato bo'lmasligi kerak
HTML_CODE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; padding: 20px; font-family: sans-serif; }
        .card { max-width: 600px; margin: auto; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header { background: #0d6efd; color: white; padding: 20px; text-align: center; }
        .alert-top { background: #fff3cd; color: #856404; padding: 10px; font-size: 12px; text-align: center; font-weight: bold; }
        .p-4 { padding: 1.5rem; }
        .btn-lang { width: 30%; font-weight: bold; }
        #res { background: white; border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-top: 20px; min-height: 100px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="card">
        <div class="alert-top">⚠️ OGOHLANTIRISH: SHIFOKOR MASLAHATI SHART!</div>
        <div class="header"><h3>💊 MedAssist Pro AI</h3></div>
        <div class="p-4 bg-white">
            <input type="text" id="d" class="form-control mb-3" placeholder="Dori nomini yozing...">
            <div class="d-flex justify-content-between mb-3">
                <button onclick="send('uzbekcha')" class="btn btn-outline-primary btn-lang">O'zbek</button>
                <button onclick="send('ruscha')" class="btn btn-outline-info btn-lang">Русский</button>
                <button onclick="send('inglizcha')" class="btn btn-outline-dark btn-lang">English</button>
            </div>
            <div id="res">Ma'lumot uchun tilni tanlang.</div>
        </div>
    </div>
    <script>
        async function send(l) {
            const d = document.getElementById('d').value;
            if(!d) return alert("Dori nomini yozing!");
            document.getElementById('res').innerText = "Qidirilmoqda...";
            try {
                const r = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({dori: d, til: l})
                });
                const resData = await r.json();
                document.getElementById('res').innerText = resData.result;
            } catch (e) {
                document.getElementById('res').innerText = "Xatolik yuz berdi.";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/ask', methods=['POST'])
def ask_ai():
    try:
        data = request.json
        dori = data.get('dori')
        til = data.get('til')
        
        # AI uchun qat'iy ko'rsatma
        msg = f"Siz professional farmatsevtsiz. {dori} haqida tarkibi, dozasi va foydasi haqida FAQAT {til}da javob bering. To'qib chiqarmang. Oxirida shifokor maslahati kerakligini ayting."

        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": msg}],
            temperature=0.0
        )
        return jsonify({'result': chat.choices[0].message.content})
    except Exception as e:
        return jsonify({'result': f"Xatolik: {str(e)}"}), 500

if __name__ == '__main__':
    # Render uchun to'g'ri port sozlamasi
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
