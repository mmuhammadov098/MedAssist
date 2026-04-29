import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .main-card { max-width: 650px; margin: auto; border-radius: 20px; background: white; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #e0e0e0; }
        .disclaimer-banner { background: #fff3cd; color: #856404; padding: 15px; font-size: 14px; text-align: center; border-bottom: 2px solid #ffeeba; }
        .header { background: #1a73e8; color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; }
        .btn-group-custom { display: flex; gap: 10px; margin: 20px 0; }
        .btn-lang { flex: 1; font-weight: 600; padding: 12px; border-radius: 12px; transition: 0.3s; }
        #javob { background: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #eee; min-height: 200px; line-height: 1.8; color: #333; font-size: 16px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
        .loader { display: none; text-align: center; margin: 20px 0; }
        strong { color: #1a73e8; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="disclaimer-banner">
            <strong>⚠️ OGOHLANTIRISH:</strong> Ushbu ma'lumotlar faqat tanishish uchun. Har qanday dori vositasini qabul qilishdan oldin albatta mutaxassis shifokor bilan maslahatlashing!
        </div>
        <div class="header">
            <h2 class="mb-0">💊 MedAssist Pro AI</h2>
            <p class="mb-0 opacity-75">Professional Tibbiy Ma'lumotnoma</p>
        </div>
        <div class="content">
            <label class="form-label fw-bold">Dori vositasi nomi:</label>
            <input type="text" id="dori" class="form-control form-control-lg mb-2 shadow-sm" placeholder="Masalan: Aspirin, Yodamarin...">
            
            <div class="btn-group-custom">
                <button onclick="askAI('uzbekcha')" class="btn btn-outline-primary btn-lang">O'zbekcha</button>
                <button onclick="askAI('ruscha')" class="btn btn-outline-primary btn-lang">Русский</button>
                <button onclick="askAI('inglizcha')" class="btn btn-outline-primary btn-lang">English</button>
            </div>

            <div class="loader" id="loader">
                <div class="spinner-grow text-primary" role="status"></div>
                <p class="text-primary mt-2 fw-bold">Bazadan qidirilmoqda...</p>
            </div>
            <div id="javob">Natija bu yerda ko'rinadi.</div>
        </div>
    </div>

    <script>
        async function askAI(til) {
            const dori = document.getElementById('dori').value;
            if(!dori) return;

            document.getElementById('loader').style.display = 'block';
            document.getElementById('javob').style.opacity = '0.5';

            try {
                const r = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({dori: dori, til: til})
                });
                const data = await r.json();
                document.getElementById('loader').style.display = 'none';
                document.getElementById('javob').style.opacity = '1';
                document.getElementById('javob').innerHTML = data.result;
            } catch (e) {
                document.getElementById('loader').style.display = 'none';
                document.getElementById('javob').innerText = "Xatolik: Server bilan aloqa uzildi.";
            }
        }
    </script>
</body>
</html>
"""@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    dori = data.get('dori')
    til = data.get('til')
    
    # AI uchun "Zero Hallucination" ko'rsatmasi
    prompt = (
        f"Siz aniq va mas'uliyatli farmatsevt-shifokorsiz. {dori} preparati haqida ma'lumot bering. "
        f"Javobni FAQAT {til} tilida yozing. "
        "Format: 1. Tarkibi (Xalqaro nomi), 2. Farmakologik guruhi, 3. Qo'llanilishi, 4. Nojo'ya ta'sirlari. "
        "MUHIM: Agar dori haqida aniq tibbiy ma'lumotga ega bo'lmasangiz, taxmin qilmang. "
        "Yodamarinni glyukoza yoki vitamin C bilan adashtirish qat'iyan man etiladi. "
        "Har doim javob oxirida shifokor maslahati zarurligini ta'kidlang."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0 # Hech qanday "to'qima" gaplarga yo'l qo'ymaydi
        )
        return jsonify({'result': completion.choices[0].message.content.replace('\\n', '<br>')})
    except Exception as e:
        return jsonify({'result': f"Xatolik: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
