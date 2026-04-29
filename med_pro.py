import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# HTML ni o'zgaruvchiga olamiz (Xato chiqmasligi uchun ehtiyotkorlik bilan)
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .main-card { max-width: 600px; margin: auto; border-radius: 20px; background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #007bff; color: white; padding: 25px; text-align: center; }
        .content { padding: 25px; }
        .lang-btns { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        #javob { background: #f8f9fa; padding: 20px; border-radius: 10px; min-height: 150px; line-height: 1.6; border: 1px solid #eee; }
        .loader { display: none; text-align: center; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="header"><h3>💊 MedAssist Pro AI</h3></div>
        <div class="content">
            <input type="text" id="dori" class="form-control form-control-lg mb-3" placeholder="Dori nomini yozing...">
            
            <p class="text-center small text-muted">Tilni tanlang:</p>
            <div class="lang-btns">
                <button onclick="askAI('uz')" class="btn btn-outline-primary">O'zbekcha</button>
                <button onclick="askAI('ru')" class="btn btn-outline-primary">Русский</button>
                <button onclick="askAI('en')" class="btn btn-outline-primary">English</button>
            </div>

            <div class="loader" id="loader">
                <div class="spinner-border text-primary"></div>
                <p>Qidirilmoqda...</p>
            </div>
            <div id="javob">Natija bu yerda chiqadi.</div>
        </div>
    </div>

    <script>
        async function askAI(til) {
            const dori = document.getElementById('dori').value;
            if(!dori) return alert("Dori nomini kiriting!");
            document.getElementById('loader').style.display = 'block';
            document.getElementById('javob').innerText = '';
            try {
                const r = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({dori: dori, til: til})
                });
                const data = await r.json();
                document.getElementById('loader').style.display = 'none';
                document.getElementById('javob').innerHTML = data.result;
            } catch (e) {
                document.getElementById('loader').style.display = 'none';
                document.getElementById('javob').innerText = "Xatolik yuz berdi.";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        dori = data.get('dori')
        til = data.get('til')
        
        prompt = (
            f"Siz farmatsevtsiz. {dori} preparati haqida ma'lumot bering. "
            f"Javobni FAQAT {til} tilida yozing. "
            "To'qib chiqarmang. Tarkibi, ishlatilishi va nojo'ya ta'sirlarini yozing. "
            "Oxirida shifokor maslahati zarurligini ayting."
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return jsonify({'result': completion.choices[0].message.content.replace('\\n', '<br>')})
    except Exception as e:
        return jsonify({'result': f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
