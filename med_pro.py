import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# Render-dagi Environment Variables-dan GROQ_API_KEY-ni oladi
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #eef2f3; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header { background: #1a73e8; color: white; padding: 25px; text-align: center; border-radius: 20px 20px 0 0; }
        .btn-primary { background: #1a73e8; border: none; padding: 12px; border-radius: 10px; font-weight: bold; }
        #javob { background: #fff; border-left: 5px solid #1a73e8; padding: 15px; margin-top: 20px; border-radius: 8px; font-size: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h3>💊 MedAssist Pro</h3>
        </div>
        <div class="card-body">
            <div class="mb-3">
                <label class="form-label">Dori nomi:</label>
                <input type="text" id="dori" class="form-control" placeholder="Masalan: Yodamarin">
            </div>
            <button onclick="askAI()" class="btn btn-primary w-100">Ma'lumot olish</button>
            <div id="javob" style="display:none;">
                <strong>Natija:</strong>
                <p id="resultText"></p>
            </div>
        </div>
    </div>

    <script>
        async function askAI() {
            const dori = document.getElementById('dori').value;
            const resDiv = document.getElementById('javob');
            const resText = document.getElementById('resultText');
            
            if(!dori) return alert("Dori nomini yozing");
            
            resDiv.style.display = 'block';
            resText.innerText = "AI qidirmoqda...";

            const response = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({dori: dori})
            });
            const data = await response.json();
            resText.innerText = data.result;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    dori_nomi = data.get('dori')
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Siz malakali farmatsevt shifokorsiz. Dorilar haqida aniq va tushunarli ma'lumot bering."},
                {"role": "user", "content": f"{dori_nomi} dorisi haqida o'zbek tilida ma'lumot ber."}
            ]
        )
        return jsonify({'result': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'result': f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
