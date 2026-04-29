const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const API_KEY = process.env.OPENAI_API_KEY;

const HTML_UI = `
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; display: flex; justify-content: center; padding: 15px; }
        .card { background: white; width: 100%; max-width: 420px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.15); overflow: hidden; }
        .header { background: #007bff; color: white; padding: 25px; text-align: center; font-size: 26px; font-weight: bold; }
        .p-3 { padding: 20px; }
        
        /* Tillar ranglari */
        .btn-uz { background: #28a745 !important; color: white; } /* Yashil */
        .btn-ru { background: #17a2b8 !important; color: white; } /* Havorang */
        .btn-en { background: #343a40 !important; color: white; } /* To'q kulrang */
        
        input, button { width: 100%; padding: 14px; margin-bottom: 12px; border-radius: 12px; border: 1px solid #ddd; font-size: 16px; transition: 0.3s; }
        button { border: none; font-weight: bold; cursor: pointer; }
        button:active { transform: scale(0.98); }
        
        .btn-search { background: #007bff; color: white; margin-top: 5px; font-size: 18px; }
        .lang-group { display: flex; gap: 8px; margin-bottom: 10px; }
        .lang-group button { font-size: 12px; padding: 10px 5px; }

        .result-box { background: #f9f9f9; border-left: 6px solid #007bff; padding: 18px; margin-top: 15px; border-radius: 8px; min-height: 100px; }
        .blue-label { color: #007bff; font-weight: 900; display: block; margin-top: 15px; border-bottom: 1px solid #eee; padding-bottom: 3px; }
        
        .alarm-card { background: #fff3cd; padding: 18px; border-radius: 20px; margin-top: 25px; border: 2px solid #ffeeba; }
        .status-text { text-align: center; font-size: 13px; color: #856404; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">💊 MedAssist Pro</div>
        <div class="p-3">
            <input type="text" id="drugName" placeholder="Dori nomini kiriting...">
            
            <div class="lang-group">
                <button class="btn-uz" onclick="setL('uz')">O'ZBEKCHA</button>
                <button class="btn-ru" onclick="setL('ru')">РУССКИЙ</button>
                <button class="btn-en" onclick="setL('en')">ENGLISH</button>
            </div>

            <button class="btn-search" onclick="getInfo()">🔍 QIDIRISH</button>

            <div id="res" class="result-box">Ma'lumot bu yerda chiqadi...</div>

            <div class="alarm-card">
                <h4 style="margin:0 0 12px 0; text-align:center">⏰ KUNLIK ESLATMA</h4>
                <input type="time" id="atime">
                <button onclick="saveA()" style="background:#ffc107; color:#212529">SAQLASH (HAR KUNI)</button>
                <p id="astatus" class="status-text"></p>
            </div>
        </div>
    </div>

    <script>
        let lang = 'uz';
        function setL(l) { lang = l; alert("Tanlangan til: " + l.toUpperCase()); }

        async function getInfo() {
            const name = document.getElementById('drugName').value;
            if(!name) return;
            const resDiv = document.getElementById('res');
            resDiv.innerHTML = "⌛ To'liq ma'lumot tayyorlanmoqda...";
            
            try {
                const r = await fetch('/drug', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},body: JSON.stringify({name, lang})
                });
                const d = await r.json();
                
                // Ma'lumotni formatlash va sarlavhalarni ajratish
                let text = d.text
                    .replace(/TARKIBI:/gi, '<span class="blue-label">TARKIBI:</span>')
                    .replace(/DOZASI:/gi, '<span class="blue-label">DOZASI:</span>')
                    .replace(/FOYDASI:/gi, '<span class="blue-label">FOYDASI:</span>')
                    .replace(/ZARARI:/gi, '<span class="blue-label">ZARARI:</span>');
                
                resDiv.innerHTML = text;
            } catch(e) { resDiv.innerHTML = "❌ Aloqa xatosi!"; }
        }

        function saveA() {
            const t = document.getElementById('atime').value;
            if(!t) return;
            localStorage.setItem('daily_med_time', t);
            document.getElementById('astatus').innerText = "✅ Har kuni " + t + " da eslatiladi";
            alert("Eslatma har kunlik rejimga o'rnatildi!");
        }

        // Har minutda tekshirish
        setInterval(() => {
            const savedTime = localStorage.getItem('daily_med_time');
            if(!savedTime) return;
            
            const now = new Date();
            const currentTime = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            
            if(currentTime === savedTime) {
                // Ovoz o'rniga alert va tebranish (Vibration API)
                if (navigator.vibrate) navigator.vibrate([500, 200, 500]);
                alert("🚨 KUNLIK ESLATMA: Doringizni ichish vaqti bo'ldi! (" + savedTime + ")");
            }
        }, 60000);

        // Sahifa yuklanganda holatni ko'rsatish
        window.onload = () => {
            const s = localStorage.getItem('daily_med_time');
            if(s) document.getElementById('astatus').innerText = "✅ Har kuni " + s + " da eslatiladi";
        };
    </script>
</body>
</html>
;

app.get('/', (req, res) => res.send(HTML_UI));

app.post("/drug", async (req, res) => {
  const { name, lang } = req.body;
  // AI ga kengaytirilgan va batafsil buyruq (Prompt)
  const prompt = Dori nomi: ${name}. Til: ${lang}. 
  Iltimos, dori haqida ilmiy va batafsil ma'lumot ber. 
  Javobni aniq shu 4 ta sarlavha ostida yoz va har bir sarlavhadan keyin kamida 3-4 gapdan iborat ma'lumot bo'lsin:
  1. TARKIBI: (kimyoviy va asosiy moddalari)
  2. DOZASI: (bolalar va kattalar uchun alohida)
  3. FOYDASI: (qaysi kasalliklarga qarshi)
  4. ZARARI: (nojo'ya ta'sirlari va kimlarga mumkin emasligi)
  Oxirida: "Muhim: Shifokor bilan maslahatlashing!" deb yoz.;

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": Bearer ${API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.7
      })
    });
    const data = await response.json();
    res.json({ text: data.choices[0].message.content });
  } catch (e) {
    res.status(500).json({ text: "AI javob bermadi." });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Loyiha ishladi!"));
