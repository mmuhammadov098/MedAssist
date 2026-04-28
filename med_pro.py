import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

# 1. AI sozlamalari
genai.configure(api_key="AIzaSyCe-WC2_SuzsBQchcRg8a-uT52rfHdMyj0")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

# 2. Ilovaning ko'rinishi (Dizayn)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #eef2f3; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header { background: #1a73e8; color: white; padding: 25px; text-align: center; border-radius: 20px 20px 0 0; }
        .btn-primary { background: #1a73e8; border: none; padding: 12px; border-radius: 10px; font-weight: bold; }
        #javob { background: #fff; border-left: 5px solid #1a73e8; padding: 15px; margin-top: 20px; border-radius: 8px; font-size: 15px; display: none; }
    </style>
</head>
<body>
<div class="card">
    <div class="header"><h3>💊 MedAssist Pro</h3></div>
    <div class="card-body p-4">
        <div class="mb-3">
            <label class="form-label fw-bold">Dori nomi:</label>
            <input type="text" id="nom" class="form-control" placeholder="Masalan: Aspirin">
        </div>
        <div class="mb-3">
            <label class="form-label fw-bold">Til:</label>
            <select id="til" class="form-select">
                <option value="O'zbek">O'zbekcha</option>
                <option value="Ruscha">Русский</option>
            </select>
        </div>
        <button onclick="qidiruv()" class="btn btn-primary w-100">AI dan ma'lumot olish</button>
        <div id="javob"></div>
    </div>
</div>

<script>
    async function qidiruv() {
        const nom = document.getElementById('nom').value;
        const til = document.getElementById('til').value;
        const box = document.getElementById('javob');
        if(!nom) return alert("Nomini yozing!");
        
        box.style.display = "block";
        box.innerHTML = "⌛ AI qidirmoqda...";

        try {
            const res = await fetch('/api', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ nom: nom, til: til })
            });
            const data = await res.json();
            box.innerHTML = "<b>Natija:</b><br>" + data.text;
        } catch (e) {
            box.innerHTML = "❌ Xatolik yuz berdi.";
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api', methods=['POST'])
def api():
    data = request.json
    prompt = f"{data['nom']} dori haqida {data['til']} tilida batafsil ma'lumot ber."
    try:
        res = model.generate_content(prompt)
        return jsonify({"text": res.text})
    except Exception as e:
        return jsonify({"text": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
