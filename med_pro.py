import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# API KEY ni tekshiramiz
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .main-card { max-width: 850px; margin: auto; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); background: white; overflow: hidden; }
        .disclaimer { background: #fff3cd; color: #856404; padding: 12px; font-size: 13px; text-align: center; font-weight: 600; border-bottom: 1px solid #ffeeba; }
        .header { background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); color: white; padding: 30px; text-align: center; }
        .search-section { padding: 30px; }
        #javob { padding: 30px; border-top: 1px solid #eee; }
        pre { white-space: pre-wrap; word-wrap: break-word; font-family: inherit; font-size: 16px; line-height: 1.7; }
        .loader { display: none; text-align: center; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="disclaimer">
            ⚠️ DIQQAT: AI ma'lumotlari faqat tanishish uchun. Shifokor maslahati shart!
        </div>
        <div class="header">
            <h2>💊 MedAssist Pro AI</h2>
            <p>UZ | RU | EN</p>
        </div>
        <div class="search-section">
            <div class="input-group">
                <input type="text" id="dori" class="form-control" placeholder="Dori nomi...">
                <button onclick="askAI()" class="btn btn-primary">Qidirish</button>
            </div>
        </div>
        <div id="javob">
            <div class="loader" id="loader">
                <div class="spinner-border text-primary"></div>
            </div>
            <div id="resultContent">Natija bu yerda ko'rinadi.</div>
        </div>
    </div>
    <script>
        async function askAI() {
            const dori = document.getElementById('dori').value;
            if(!dori) return alert("Dori nomini yozing!");
            document.getElementById('loader').style.display = 'block';
            document.getElementById('resultContent').innerHTML = '';
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({dori: dori})
                });
                const data = await response.json();
                document.getElementById('loader').style.display = 'none';
                document.getElementById('resultContent').innerHTML = '<pre>' + data.result + '</pre>';
            } catch (e) {
                document.getElementById('loader').style.display = 'none';
                document.getElementById('resultContent').innerHTML = "Xatolik yuz berdi.";
            }
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
    try:
        data = request.get_json()
        dori_nomi = data.get('dori')
        
        system_instruction = (
            "Siz professional farmatsevtsiz. Faqat aniq tibbiy faktlarni bering. "
            "Javobni 3 tilda (O'zbek, Rus, Ingliz) chiroyli formatda bering. "
            "Oxirida shifokor maslahati shartligini eslatib o'ting."
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"{dori_nomi} haqida ma'lumot ber."}
            ],
            temperature=0.1
        )
        return jsonify({'result': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'result': f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    # Render uchun eng xavfsiz port sozlamasi
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
