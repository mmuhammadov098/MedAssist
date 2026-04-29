import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# API ulanishi - xatolik chiqmasligi uchun tekshiruv bilan
GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; padding: 15px; }
        .card { max-width: 400px; margin: auto; border-radius: 15px; border: none; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        #res { background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0; min-height: 40px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card p-3 mt-4">
        <h5 class="text-center text-primary">💊 MedAssist AI</h5>
        <input type="text" id="d" class="form-control mb-2" placeholder="Dori nomi...">
        <button onclick="s()" class="btn btn-primary w-100">Qidirish</button>
        <div id="res">Natija...</div>
        
        <div class="p-3 bg-light rounded">
            <h6 class="text-center">⏰ Eslatma</h6>
            <input type="time" id="t" class="form-control mb-2">
            <button onclick="set()" class="btn btn-warning w-100 btn-sm">Eslatmani yoqish</button>
        </div>
    </div>

    <script>
        async function s() {
            const n = document.getElementById('d').value;
            if(!n) return;
            document.getElementById('res').innerText = "⌛...";
            try {
                const r = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: n})
                });
                const d = await r.json();
                document.getElementById('res').innerText = d.t;
            } catch { document.getElementById('res').innerText = "Xato!"; }
        }

        function set() {
            const v = document.getElementById('t').value;
            if(!v) return;
            localStorage.setItem('med_v', v);
            alert("Eslatma qo'yildi: " + v);
        }

        setInterval(() => {
            const v = localStorage.getItem('med_v');
            const n = new Date();
            const c = n.getHours().toString().padStart(2,'0') + ":" + n.getMinutes().toString().padStart(2,'0');
            if(v === c) {
                window.speechSynthesis.speak(new SpeechSynthesisUtterance("Dori ichish vaqti bo'ldi!"));
                alert("⏰ Dori iching!");
                localStorage.removeItem('med_v');
            }
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@app.route('/ask', methods=['POST'])
def ask():
    req = request.json
    if not client: return jsonify({"t": "API Key yo'q!"})
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{req['name']} dorisi haqida faqat tarkibi va dozasi haqida 3 qator o'zbekcha yoz."}]
        )
        return jsonify({"t": res.choices[0].message.content})
    except: return jsonify({"t": "Xato yuz berdi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
