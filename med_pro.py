from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Nunito', sans-serif;
            background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 100%);
            min-height: 100vh;
            padding: 20px 15px 40px;
        }

        .card {
            background: #ffffff;
            max-width: 520px;
            margin: 0 auto;
            border-radius: 24px;
            box-shadow: 0 8px 40px rgba(0, 100, 200, 0.13);
            overflow: hidden;
            animation: fadeUp 0.5s ease;
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── HEADER ── */
        .header {
            background: linear-gradient(135deg, #0062cc, #00b4d8);
            color: white;
            padding: 24px 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }
        .header p  { font-size: 13px; opacity: 0.85; margin-top: 4px; }

        /* ── BODY ── */
        .body { padding: 24px 20px; }

        /* Search row */
        .search-row {
            display: flex;
            gap: 8px;
            margin-bottom: 14px;
        }
        .search-row input {
            flex: 1;
            padding: 13px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 15px;
            font-family: 'Nunito', sans-serif;
            transition: border 0.2s;
            outline: none;
        }
        .search-row input:focus { border-color: #0062cc; }
        .search-row input::placeholder { color: #a0aec0; }

        .btn-search {
            padding: 13px 18px;
            background: linear-gradient(135deg, #0062cc, #00b4d8);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 20px;
            cursor: pointer;
            transition: transform 0.15s, box-shadow 0.15s;
        }
        .btn-search:hover { transform: scale(1.06); box-shadow: 0 4px 14px rgba(0,98,204,0.35); }
        .btn-search:active { transform: scale(0.97); }

        /* Language buttons */
        .lang-group {
            display: flex;
            gap: 8px;
            margin-bottom: 18px;
        }
        .btn-lang {
            flex: 1;
            padding: 11px 6px;
            border: 2.5px solid transparent;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Nunito', sans-serif;
        }
        .btn-lang.uz { background: #d1fae5; color: #065f46; border-color: #6ee7b7; }
        .btn-lang.ru { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
        .btn-lang.en { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }
        .btn-lang.active { transform: scale(1.06); box-shadow: 0 3px 10px rgba(0,0,0,0.15); }
        .btn-lang.uz.active { background: #059669; color: white; border-color: #059669; }
        .btn-lang.ru.active { background: #d97706; color: white; border-color: #d97706; }
        .btn-lang.en.active { background: #dc2626; color: white; border-color: #dc2626; }

        /* Result box */
        .result {
            background: #f8faff;border: 1.5px solid #e2e8f0;
            border-left: 5px solid #0062cc;
            border-radius: 14px;
            padding: 16px;
            min-height: 80px;
            font-size: 14px;
            line-height: 1.7;
            color: #2d3748;
            margin-bottom: 16px;
            transition: all 0.3s;
        }
        .result.loading { color: #718096; font-style: italic; }

        .section-label {
            color: #0062cc;
            font-weight: 800;
            font-size: 13.5px;
            display: block;
            margin-top: 12px;
            margin-bottom: 2px;
            letter-spacing: 0.3px;
        }
        .section-label:first-child { margin-top: 0; }

        /* Warning */
        .warning {
            background: #fffbeb;
            color: #92400e;
            border: 1.5px solid #fde68a;
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 12px;
            text-align: center;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        /* Alarm box */
        .alarm-box {
            background: linear-gradient(135deg, #eff6ff, #f0fdf4);
            border: 2px dashed #93c5fd;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
        }
        .alarm-box h4 {
            font-size: 15px;
            font-weight: 800;
            color: #1e40af;
            margin-bottom: 12px;
        }
        .alarm-box input[type="time"] {
            padding: 10px 14px;
            border: 2px solid #bfdbfe;
            border-radius: 10px;
            font-size: 15px;
            font-family: 'Nunito', sans-serif;
            margin-bottom: 10px;
            width: 100%;
            outline: none;
            color: #1e3a8a;
            transition: border 0.2s;
        }
        .alarm-box input[type="time"]:focus { border-color: #3b82f6; }

        .btn-save {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #059669, #34d399);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            font-family: 'Nunito', sans-serif;
            transition: transform 0.15s, box-shadow 0.15s;
        }
        .btn-save:hover { transform: scale(1.03); box-shadow: 0 4px 14px rgba(5,150,105,0.35); }

        #alarm-status {
            margin-top: 10px;
            font-size: 13px;
            color: #065f46;
            font-weight: 600;
            min-height: 20px;
        }

        /* Spinner */
        .spinner {
            display: inline-block;
            width: 18px; height: 18px;
            border: 3px solid #bfdbfe;
            border-top-color: #0062cc;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Footer */
        .footer {
            text-align: center;
            font-size: 11.5px;
            color: #94a3b8;
            margin-top: 18px;
        }
    </style>
</head>
<body>
<div class="card">

    <!-- HEADER -->
    <div class="header">
        <h1>🛡️ MedAssist Pro</h1>
        <p>AI yordamida dori ma'lumotlari • 3 tilda</p>
    </div>

    <!-- BODY -->
    <div class="body">

        <!-- Qidiruv -->
        <div class="search-row">
            <input type="text" id="drug-input" placeholder="Dori nomini yozing... (masalan: Paracetamol)" onkeydown="if(event.key==='Enter') ask()">
            <button class="btn-search" onclick="ask()" title="Qidirish">🔍</button>
        </div>

        <!-- Til tanlash -->
        <div class="lang-group"><button class="btn-lang uz active" id="btn-uz" onclick="setL('uz')">🇺🇿 O'ZBEK</button>
            <button class="btn-lang ru"         id="btn-ru" onclick="setL('ru')">🇷🇺 РУССКИЙ</button>
            <button class="btn-lang en"         id="btn-en" onclick="setL('en')">🇺🇸 ENGLISH</button>
        </div>

        <!-- Natija -->
        <div id="result-box" class="result">
            💊 Dori nomini kiriting va qidiring...
        </div>

        <!-- Ogohlantirish -->
        <div class="warning">
            ⚠️ <strong>DIQQAT:</strong> Ma'lumotlar AI tomonidan berilgan. Dorini ichishdan oldin
            albatta <strong>shifokor bilan maslahatlashing!</strong>
        </div>

        <!-- Eslatma -->
        <div class="alarm-box">
            <h4>⏰ Dori ichish eslatmasi</h4>
            <input type="time" id="alarm-time">
            <button class="btn-save" onclick="saveAlarm()">🔔 Eslatmani saqlash</button>
            <div id="alarm-status"></div>
        </div>

    </div>

    <div class="footer">MedAssist Pro • Faqat ma'lumot uchun • © 2025</div>
</div>

<script>
    /* ─── Holat ─── */
    let currentLang = 'uz';

    /* ─── Til tanlash ─── */
    function setL(lang) {
        currentLang = lang;
        ['uz','ru','en'].forEach(l => {
            document.getElementById('btn-' + l).classList.toggle('active', l === lang);
        });
    }

    /* ─── Qidirish ─── */
    async function ask() {
        const name = document.getElementById('drug-input').value.trim();
        if (!name) {
            showResult('⚠️ Iltimos, dori nomini kiriting.', false);
            return;
        }

        // Yuklanmoqda
        showResult('<span class="spinner"></span> Qidirilmoqda, iltimos kuting...', false);
        document.getElementById('result-box').classList.add('loading');

        try {
            const res = await fetch('/get_drug', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, lang: currentLang })
            });

            if (!res.ok) throw new Error('Server xatosi: ' + res.status);

            const data = await res.json();
            if (data.error) throw new Error(data.error);

            // Matnni formatlash
            let text = data.text
                .replace(/TARKIBI:/g,  '<span class="section-label">🧪 TARKIBI:</span>')
                .replace(/DOZASI:/g,   '<span class="section-label">⚖️ DOZASI:</span>')
                .replace(/FOYDASI:/g,  '<span class="section-label">✅ FOYDASI:</span>')
                .replace(/ZARARI:/g,   '<span class="section-label">❌ ZARARI:</span>')
                .replace(/\\n/g, '<br>');

            showResult(text, true);

        } catch (err) {
            showResult('❌ Xatolik: ' + err.message, false);
        }

        document.getElementById('result-box').classList.remove('loading');
    }

    function showResult(html, isHtml) {
        const box = document.getElementById('result-box');
        if (isHtml) {
            box.innerHTML = html;
        } else {
            box.innerHTML = html; // spinner va xato ham HTML
        }
    }

    /* ─── Eslatma ─── */
    function saveAlarm() {
        const t = document.getElementById('alarm-time').value;
        if (!t) {
            document.getElementById('alarm-status').textContent = '⚠️ Vaqtni kiriting!';
            return;
        }
        localStorage.setItem('medassist_alarm', t);
        document.getElementById('alarm-status').textContent = '🔔 Eslatma ' + t + ' ga saqlandi!';

        // Bildirishnoma ruxsati
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    /* ─── Har 10 soniyada tekshirish ─── */
    setInterval(() => {const saved = localStorage.getItem('medassist_alarm');
        if (!saved) return;
        const now = new Date();
        const cur = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
        if (saved === cur) {
            // Faqat bir marta ogohlantirish (daqiqa boshida)
            if (now.getSeconds() < 11) {
                alert('🚨 VAQT BO\'LDI! DORINGIZNI ICHING!\\n(Shifokor tavsiyasiga amal qiling)');
                if (Notification.permission === 'granted') {
                    new Notification('🚨 MedAssist Pro', {
                        body: 'Dori ichish vaqti keldi!',
                        icon: 'https://cdn-icons-png.flaticon.com/512/2913/2913136.png'
                    });
                }
            }
        }
    }, 10000);

    /* ─── Saqlangan eslatmani ko'rsatish ─── */
    window.onload = () => {
        const saved = localStorage.getItem('medassist_alarm');
        if (saved) {
            document.getElementById('alarm-time').value = saved;
            document.getElementById('alarm-status').textContent = '🔔 Faol eslatma: ' + saved;
        }
    };
</script>
</body>
</html>"""


@app.route('/')
def home():
    return HTML_TEMPLATE


@app.route('/get_drug', methods=['POST'])
def get_drug():
    try:
        data = request.json
        drug_name = data.get('name', '').strip()
        lang = data.get('lang', 'uz').strip()

        if not drug_name:
            return jsonify({"error": "Dori nomi bo'sh"}), 400

        lang_map = {
            'uz': "o'zbek",
            'ru': "rus",
            'en': "ingliz"
        }
        lang_name = lang_map.get(lang, "o'zbek")

        prompt = (
            f"'{drug_name}' dorisi haqida {lang_name} tilida qisqa va aniq ma'lumot ber. "
            f"Javobni quyidagi bo'limlar bilan yoz:\n"
            f"TARKIBI: (asosiy kimyoviy modda)\n"
            f"DOZASI: (odatdagi doza)\n"
            f"FOYDASI: (asosiy qo'llanilishi)\n"
            f"ZARARI: (asosiy yon ta'sirlar)\n"
            f"Har bir bo'lim 2-3 jumladan oshmasin."
        )

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Sen tibbiy ma'lumot beruvchi yordamchisan. Faqat so'ralgan tilda javob ber. Javob qisqa, aniq va foydali bo'lsin."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.4
        )

        answer = response.choices[0].message.content
        return jsonify({"text": answer})

    except openai.AuthenticationError:
        return jsonify({"error": "OpenAI API kalit noto'g'ri yoki topilmadi"}), 401
    except openai.RateLimitError:
        return jsonify({"error": "API limiti tugadi, keyinroq urinib ko'ring"}), 429
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
