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
        body { background: #f4f7f6; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .main-card { max-width: 850px; margin: auto; border-radius: 20px; border: none; box-shadow: 0 15px 35px rgba(0,0,0,0.1); overflow: hidden; background: white; }
        .header { background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); color: white; padding: 40px 20px; text-align: center; }
        .disclaimer { background: #fff3cd; color: #856404; padding: 12px; font-size: 13px; text-align: center; border-bottom: 1px solid #ffeeba; font-weight: 500; }
        .search-section { padding: 30px; background: #fff; }
        #javob { padding: 30px; border-top: 1px solid #eee; }
        pre { white-space: pre-wrap; word-wrap: break-word; font-family: inherit; font-size: 16px; color: #2c3e50; line-height: 1.7; }
        .loader { display: none; text-align: center; padding: 30px; }
        .btn-search { background: #1a73e8; color: white; padding: 12px 30px; border-radius: 10px; font-weight: 600; border: none; }
        .btn-search:hover { background: #1557b0; color: white; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="disclaimer">
            ⚠️ DIQQAT: AI tomonidan berilgan ma'lumotlar faqat tanishish uchun. Dori qabul qilishdan oldin albatta shifokor bilan maslahatlashing!
        </div>

        <div class="header">
            <h2>💊 MedAssist Pro AI</h2>
            <p>Ko'p tilli tibbiy yordamchi (UZ | RU | EN)</p>
        </div>
        
        <div class="search-section">
            <div class="input-group mb-3">
                <input type="text" id="dori" class="form-control form-control-lg shadow-none" placeholder="Dori nomini kiriting...">
                <button onclick="askAI()" class="btn btn-search">Qidirish</button>
            </div>
        </div>

        <div id="javob">
            <div class="loader" id="loader">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-3">Ma'lumotlar tekshirilmoqda, iltimos kuting...</p>
            </div>
            <div id="resultContent">
                <p class="text-muted text-center italic">Qidiruv natijasi bu yerda ko'rinadi.</p>
            </div>
        </div>
    </div>

    <script>
        async function askAI() {
            const dori = document.getElementById('dori').value;
            if(!dori) return alert("Iltimos, dori nomini yozing!");

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
                document.getElementById('resultContent').innerHTML = "Xatolik: Server bilan aloqa uzildi.";
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
    data = request.json
    dori_nomi = data.get('dori')
    
    # AI uchun qat'iy va xatosiz ko'rsatma
    system_instruction = (
        "Siz tajribali farmatsevt va tibbiy maslahatchisiz. "
        "Faqat tasdiqlangan va aniq tibbiy ma'lumotlarni taqdim eting. "
        "Agar dori haqida ma'lumotni aniq bilmasangiz, to'qib chiqarmang va 'Ma'lumot topilmadi' deb javob bering. "
        "Har doim javobingizning oxirida 'Iltimos, dori qabul qilishdan oldin shifokor bilan maslahatlashing' deb yozing. "
        "Javobni quyidagi 3 tilda bering:\n\n"
        "🇺🇿 O'ZBEKCHA:\n(Tarkibi, Qo'llanilishi, Dozasi, Nojo'ya ta'sirlari)\n\n"
        "🇷🇺 РУССКИЙ:\n(Состав, Применение, Дозировка, Побочные эффекты)\n\n"
        "🇬🇧 ENGLISH:\n(Ingredients, Usage, Dosage, Side effects)"
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"{dori_nomi} dorisi haqida 3 tilda batafsil ma'lumot ber."}
            ],
            temperature=0.1 # Faktlar aniq bo'lishi uchun
        )
        return jsonify({'result': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'result': f"Xatolik yuz berdi: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
