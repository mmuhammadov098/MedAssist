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
        body { font-family: sans-serif; background: #f8f9fa; display: flex; justify-content: center; padding: 15px; margin: 0; }
        .card { background: white; width: 100%; max-width: 400px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; }
        .p-3 { padding: 20px; }
        .btn-uz { background: #28a745 !important; color: white; flex: 1; }
        .btn-ru { background: #17a2b8 !important; color: white; flex: 1; }
        .btn-en { background: #343a40 !important; color: white; flex: 1; }
        input, button { width: 100%; padding: 14px; margin-bottom: 10px; border-radius: 12px; border: 1px solid #ddd; box-sizing: border-box; font-size: 16px; }
        button { border: none; font-weight: bold; cursor: pointer; }
        .lang-group { display: flex; gap: 5px; margin-bottom: 10px; }
        .btn-search { background: #007bff; color: white; }
        .result-box { background: #fff; border-left: 6px solid #007bff; padding: 15px; margin-top: 15px; border-radius: 8px; min-height: 80px; font-size: 14px; }
        .blue-label { color: #007bff; font-weight: bold; display: block; margin-top: 10px; }
        .alarm-card { background: #fff3cd; padding: 15px; border-radius: 15px; margin-top: 20px; border: 1px dashed #ffc107; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">💊 MedAssist Pro</div>
        <div class="p-3">
            <input type="text" id="drugIn" placeholder="Dori nomi...">
            <div class="lang-group">
                <button class="btn-uz" onclick="setL('uz')">O'ZBEK</button>
                <button class="btn-ru" onclick="setL('ru')">РУССКИЙ</button>
                <button class="btn-en" onclick="setL('en')">ENGLISH</button>
            </div>
            <button class="btn-search" onclick="find()">🔍 QIDIRISH</button>
            <div id="out" class="result-box">Natija kutilmoqda...</div>
            <div class="alarm-card">
                <h4 style="margin:0 0 10px 0; text-align:center">⏰ KUNLIK ESLATMA</h4>
                <input type="time" id="alTm">
                <button onclick="saveAl()" style="background:#ffc107; color:black">SAQLASH</button>
                <p id="alSt" style="text-align:center; font-size:12px; margin-top:5px; font-weight:bold"></p>
            </div>
        </div>
    </div>
    <script>
        let L = 'uz';
        function setL(l) { L = l; alert("Til: " + l.toUpperCase()); }
        async function find() {
            const n = document.getElementById('drugIn').value;
            if(!n) return;
            document.getElementById('out').innerHTML = "⌛ AI qidirmoqda...";
            try {
                const r = await fetch('/drug', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: n, lang: L})
                });
                const d = await r.json();
                let f = d.text.replace(/TARKIBI:/gi, '<span class="blue-label">TARKIBI:</span>')
                             .replace(/DOZASI:/gi, '<span class="blue-label">DOZASI:</span>')
                             .replace(/FOYDASI:/gi, '<span class="blue-label">FOYDASI:</span>')
                             .replace(/ZARARI:/gi, '<span class="blue-label">ZARARI:</span>');document.getElementById('out').innerHTML = f;
            } catch(e) { document.getElementById('out').innerHTML = "❌ Xatolik!"; }
        }
        function saveAl() {
            const t = document.getElementById('alTm').value;
            if(!t) return;
            localStorage.setItem('med_time_daily', t);
            document.getElementById('alSt').innerText = "✅ Har kuni " + t + " da";
            alert("Eslatma saqlandi!");
        }
        setInterval(() => {
            const s = localStorage.getItem('med_time_daily');
            if(!s) return;
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            if(cur === s) alert("🚨 VAQT BO'LDI! Doringizni iching!");
        }, 30000);
        window.onload = () => {
            const s = localStorage.getItem('med_time_daily');
            if(s) document.getElementById('alSt').innerText = "✅ Har kuni " + s + " da";
        };
    </script>
</body>
</html>
;

app.get('/', (req, res) => res.send(HTML_UI));

app.post("/drug", async (req, res) => {
  const { name, lang } = req.body;
  const prompt = Dori nomi: \${name}. Til: \${lang}. Batafsil ma'lumot ber (har bo'limda 3-4 gap): TARKIBI, DOZASI, FOYDASI, ZARARI.;
  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Authorization": \Bearer \${API_KEY}\`, "Content-Type": "application/json" },
      body: JSON.stringify({ model: "gpt-4o-mini", messages: [{ role: "user", content: prompt }] })
    });
    const data = await response.json();
    res.json({ text: data.choices[0].message.content });
  } catch (e) { res.status(500).json({ text: "AI xatosi" }); }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Live!"));
