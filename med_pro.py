from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f7; display: flex; justify-content: center; padding: 10px; margin: 0; }
        .card { background: white; width: 100%; max-width: 450px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); overflow: hidden; margin-top: 10px; border: 1px solid #d1d9e6; }
        .header { background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 25px; text-align: center; font-size: 24px; font-weight: 800; letter-spacing: 1px; }
        .p-3 { padding: 20px; }
        input, button { width: 100%; padding: 14px; margin-bottom: 12px; border-radius: 12px; border: 1px solid #ced4da; box-sizing: border-box; font-size: 16px; transition: 0.3s; }
        input:focus { border-color: #007bff; outline: none; box-shadow: 0 0 8px rgba(0,123,255,0.25); }
        .btn-blue { background: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,123,255,0.2); }
        .btn-blue:hover { background: #0056b3; transform: translateY(-2px); }
        
        /* Tillar rangi endi aniq o'zgardi */
        .lang-group { display: flex; gap: 8px; margin-bottom: 15px; }
        .btn-lang { flex: 1; border: none; color: white; font-weight: bold; cursor: pointer; padding: 12px; border-radius: 10px; font-size: 12px; opacity: 0.7; }
        .btn-lang.active { opacity: 1; transform: scale(1.05); border: 2px solid #fff; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
        .uz { background: #28a745 !important; } /* Yashil */
        .ru { background: #ffc107 !important; color: #000 !important; } /* Sariq */
        .en { background: #dc3545 !important; } /* Qizil */
        
        .result { background: #f8f9fa; border-left: 6px solid #007bff; padding: 18px; margin-top: 15px; border-radius: 10px; font-size: 15px; line-height: 1.6; color: #333; }
        .blue-t { color: #0056b3; font-weight: 800; display: block; margin-top: 12px; border-bottom: 1px solid #dee2e6; padding-bottom: 4px; }
        .warning { background: #fff3cd; color: #856404; padding: 15px; border-radius: 12px; margin-top: 20px; border: 1px solid #ffeeba; font-size: 13px; font-weight: bold; text-align: center; }
        
        .alarm-box { background: #e8f4fd; padding: 20px; border-radius: 20px; margin-top: 20px; border: 2px dashed #007bff; }
        .alarm-box h4 { margin: 0 0 10px 0; color: #0056b3; display: flex; align-items: center; justify-content: center; gap: 8px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">🛡 MedAssist Pro</div>
        <div class="p-3">
            <input type="text" id="drug" placeholder="Dori nomini kiriting (masalan: Analgin)">
            
            <div class="lang-group">
                <button id="l_uz" class="btn-lang uz active" onclick="setL('uz')">O'ZBEK</button>
                <button id="l_ru" class="btn-lang ru" onclick="setL('ru')">РУССКИЙ</button>
                <button id="l_en" class="btn-lang en" onclick="setL('en')">ENGLISH</button>
            </div>
            
            <button class="btn-blue" onclick="ask()">🔍 MA'LUMOT OLISH</button>
            
            <div id="out" class="result">Dori haqida ishonchli ma'lumot bu yerda chiqadi...</div>
            
            <div class="warning">
                ⚠️ DIQQAT: Ushbu ma'lumotlar sun'iy intellekt tomonidan tayyorlangan. Dorini ichishdan oldin ALBATTA SHIFOKOR BILAN MASLAHATLASHING!
            </div><div class="alarm-box">
                <h4>⏰ ESLATMA O'RNATISH</h4>
                <input type="time" id="tm">
                <button onclick="save()" style="background:#28a745; color:white; border:none;">ESLATMANI SAQLASH</button>
                <p id="st" style="font-size:13px; font-weight:bold; margin-top:8px; color:#28a745; text-align:center;"></p>
            </div>
        </div>
    </div>

    <script>
        let L = 'uz';
        function setL(l) { 
            L = l; 
            document.querySelectorAll('.btn-lang').forEach(b => b.classList.remove('active'));
            document.getElementById('l_' + l).classList.add('active');
        }

        async function ask() {
            const n = document.getElementById('drug').value;
            if(!n) return;
            document.getElementById('out').innerHTML = "⌛ AI tahlil qilmoqda, kuting...";
            try {
                const res = await fetch('/get_drug', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: n, lang: L})
                });
                const data = await res.json();
                let text = data.text.replace(/TARKIBI:/gi, '<span class="blue-t">🧪 TARKIBI:</span>')
                                    .replace(/DOZASI:/gi, '<span class="blue-t">⚖️ DOZASI:</span>')
                                    .replace(/FOYDASI:/gi, '<span class="blue-t">✅ FOYDASI:</span>')
                                    .replace(/ZARARI:/gi, '<span class="blue-t">❌ ZARARI:</span>');
                document.getElementById('out').innerHTML = text;
            } catch(e) { document.getElementById('out').innerHTML = "❌ Xatolik: Internetni tekshiring."; }
        }

        function save() {
            const t = document.getElementById('tm').value;
            if(!t) return;
            localStorage.setItem('med_time', t);
            document.getElementById('st').innerText = "🔔 Eslatma " + t + " ga o'rnatildi!";
            
            if (Notification.permission !== 'granted') {
                Notification.requestPermission();
            }
        }

        setInterval(() => {
            const s = localStorage.getItem('med_time');
            if(!s) return;
            const now = new Date();
            const cur = now.getHours().toString().padStart(2,'0') + ":" + now.getMinutes().toString().padStart(2,'0');
            if(cur === s) {
                new Notification("🚨 VAQT BO'LDI!", { body: "Doringizni ichish vaqti keldi!", icon: "/logo.jpg" });
                alert("🚨 VAQT BO'LDI! Doringizni iching!");
            }
        }, 10000);
    </script>
</body>
</html>
