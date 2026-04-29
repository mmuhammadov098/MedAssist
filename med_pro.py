import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Foydalanuvchi interfeysi (UI)
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 20px; font-family: 'Segoe UI', sans-serif; }
        .main-card { max-width: 600px; margin: auto; border-radius: 20px; background: white; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; }
        .disclaimer { background: #fff3cd; color: #856404; padding: 12px; font-size: 13px; text-align: center; font-weight: bold; border-bottom: 1px solid #ffeeba; }
        .content { padding: 25px; }
        .btn-group-til { display: flex; gap: 10px; margin-bottom: 20px; }
        .btn-til { flex: 1; font-weight: 600; border-radius: 12px; padding: 12px; }
        #javob { background: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; min-height: 200px; line-height: 1.8; font-size: 16px; white-space: pre-wrap; color: #333; }
        .loader { display: none; text-align: center; margin: 15px 0; }
        .footer-note { font-size: 11px; color: #6c757d; margin-top: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="disclaimer">⚠️ SHIFOKOR MASLAHATI SHART! AI ADASHISHI MUMKIN.</div>
        <div class="header"><h3>💊 MedAssist Pro AI</h3></div>
        <div class="content">
            <label class="form-label fw-bold">Dori nomini kiriting:</label>
            <input type="text" id="dori" class="form-control form-control-lg mb-3 shadow-sm" placeholder="Masalan: Analgin, Aspirin...">
            
            <p class="text-center small text-muted mb-2">Javob tilini tanlang:</p>
            <div class="btn-group-til">
                <button onclick="askAI('uzbekcha')" class="btn btn-primary btn-til shadow-sm">O'zbekcha</button>
                <button onclick="askAI('ruscha')" class="btn btn-info text-white btn-til shadow-sm">Русский</button>
                <button onclick="askAI('inglizcha')" class="btn btn-dark btn-til shadow-sm">English</button>
            </div>

            <div class="loader" id="loader">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 fw-bold">Tahlil qilinmoqda...</p>
            </div>
            
            <div id="javob">Dori haqida ma'lumot olish uchun til tugmasini bosing.</div>
            <div class="footer-note">© 2026 MedAssist Pro - Professional Tibbiy Ma'lumotnoma</div>
        </div>
    </div>

    <script>
        async function askAI(til) {
            const dori = document.getElementById('dori').value;
            if(!dori) { alert("Iltimos, dori nomini yozing!"); return; }

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
                document.getElementById('javob').innerText = data.result;
            } catch (e) {
                document.getElementById('loader').style.display = 'none';
                document.getElementById('javob').innerText = "Xatolik yuz berdi. Internetni tekshiring.";
            }
        }
    </script>
</body>
</html>
"""@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        dori = data.get('dori')
        til = data.get('til')
        
        # AIga o'ta qat'iy ko'rsatma (Zero-Hallucination)
        system_prompt = (
            f"Siz professional farmatsevt va shifokorsiz. "
            f"Javobni FAQAT {til} tilida bering. "
            "Dori haqida quyidagi tartibda ma'lumot bering:\n"
            "1. Tarkibi va xalqaro nomi.\n"
            "2. Asosiy qo'llanilishi.\n"
            "3. Tavsiya etiladigan dozasi.\n"
            "4. Nojo'ya ta'sirlari.\n"
            "MUHIM: Agar ma'lumot aniq bo'lmasa, to'qib chiqarmang. "
            "Har doim javob oxirida 'Bu ma'lumotlar tanishish uchun, shifokor bilan maslahatlashing' deb yozing."
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": dori}],
            temperature=0.0
        )
        return jsonify({'result': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'result': f"Server xatosi: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
