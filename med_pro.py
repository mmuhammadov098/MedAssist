import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Dori bazasi
MED_DATA = {
    "yodamarin": {
        "uz": "Yodamarin - yod tanqisligini oldini oluvchi dori. Tarkibi: Kaliy yodid.",
        "ru": "Йодомарин - для профилактики дефицита йода. Состав: Калия йодид.",
        "en": "Yodamarin - prevents iodine deficiency. Composition: Potassium iodide."
    },
    "analgin": {
        "uz": "Analgin - og'riq qoldiruvchi dori. Tarkibi: Metamizol natriy.",
        "ru": "Анальгин - обезболивающее средство. Состав: Метамизол натрия.",
        "en": "Analgin - pain relief medicine. Composition: Metamizole sodium."
    }
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAssist Pro</title>
    <link rel="icon" href="https://img.icons8.com/color/96/pill.png" type="image/png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding: 20px; font-family: sans-serif; }
        .card { max-width: 500px; margin: auto; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none; }
        .header { background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 20px 20px 0 0; }
        .btn-l { width: 32%; font-weight: bold; }
        #res { background: white; padding: 15px; border-radius: 10px; min-height: 100px; margin-top: 15px; border: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <img src="https://img.icons8.com/color/96/pill.png" width="40" class="mb-2">
            <h4>MedAssist Pro</h4>
        </div>
        <div class="p-4 bg-white">
            <input type="text" id="inp" class="form-control mb-3" placeholder="Dori nomi...">
            <div class="d-flex justify-content-between">
                <button onclick="get('uz')" class="btn btn-primary btn-l">O'zbek</button>
                <button onclick="get('ru')" class="btn btn-info text-white btn-l">Русский</button>
                <button onclick="get('en')" class="btn btn-dark btn-l">English</button>
            </div>
            <div id="res">Natija...</div>
            <p class="text-danger mt-3 small text-center fw-bold">⚠️ SHIFOKOR MASLAHATI SHART!</p>
        </div>
    </div>
    <script>
        function get(l) {
            const d = document.getElementById('inp').value.toLowerCase().trim();
            if(!d) return alert("Nomini yozing!");
            fetch('/data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n: d, l: l})
            }).then(r => r.json()).then(data => {
                document.getElementById('res').innerText = data.t;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/data', methods=['POST'])
def data():
    req = request.json
    d = MED_DATA.get(req.get('n'))
    if d:
        return jsonify({"t": d.get(req.get('l'))})
    return jsonify({"t": "Topilmadi."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
