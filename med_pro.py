import logging
from flask import Flask, request, jsonify
import anthropic
import os

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(name)

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MedAssist Pro</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
  :root {
    --blue:#0062cc; --blue2:#00b4d8;
    --green:#059669; --red:#dc2626; --yellow:#d97706;
    --bg:#eef6ff; --card:#ffffff;
    --text:#1e293b; --muted:#64748b; --border:#e2e8f0;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Nunito',sans-serif; background:var(--bg); min-height:100vh; padding:20px 14px 50px; }
  .card { background:var(--card); max-width:520px; margin:0 auto; border-radius:24px; box-shadow:0 8px 40px rgba(0,98,204,0.13); overflow:hidden; animation:fadeUp .4s ease; }
  @keyframes fadeUp { from{opacity:0;transform:translateY(28px)} to{opacity:1;transform:translateY(0)} }
  .header { background:linear-gradient(135deg,var(--blue),var(--blue2)); color:white; padding:22px 20px; text-align:center; }
  .header h1 { font-size:23px; font-weight:900; }
  .header p  { font-size:12.5px; opacity:.85; margin-top:4px; }
  .body { padding:22px 18px; }
  .search-row { display:flex; gap:8px; margin-bottom:12px; }
  .search-row input { flex:1; padding:13px 15px; border:2px solid var(--border); border-radius:12px; font-size:15px; font-family:'Nunito',sans-serif; outline:none; transition:border .2s; color:var(--text); }
  .search-row input:focus { border-color:var(--blue); }
  .search-row input::placeholder { color:#a0aec0; }
  .btn-go { padding:13px 17px; background:linear-gradient(135deg,var(--blue),var(--blue2)); color:white; border:none; border-radius:12px; font-size:20px; cursor:pointer; transition:transform .15s,box-shadow .15s; }
  .btn-go:hover { transform:scale(1.07); box-shadow:0 4px 14px rgba(0,98,204,.35); }
  .btn-go:disabled { opacity:.5; cursor:not-allowed; transform:none; }
  .lang-group { display:flex; gap:7px; margin-bottom:16px; }
  .btn-lang { flex:1; padding:10px 5px; border:2.5px solid transparent; border-radius:10px; font-size:12.5px; font-weight:800; cursor:pointer; transition:all .2s; font-family:'Nunito',sans-serif; }
  .btn-lang.uz { background:#d1fae5; color:#065f46; border-color:#6ee7b7; }
  .btn-lang.ru { background:#fef3c7; color:#92400e; border-color:#fcd34d; }
  .btn-lang.en { background:#fee2e2; color:#991b1b; border-color:#fca5a5; }
  .btn-lang.uz.active { background:var(--green); color:white; border-color:var(--green); }
  .btn-lang.ru.active { background:var(--yellow); color:white; border-color:var(--yellow); }
  .btn-lang.en.active { background:var(--red); color:white; border-color:var(--red); }
  .result { background:#f8faff; border:1.5px solid var(--border); border-left:5px solid var(--blue); border-radius:14px; padding:16px; min-height:90px; font-size:14px; line-height:1.75; color:var(--text); margin-bottom:14px; }
  .sec { color:var(--blue); font-weight:800; font-size:13.5px; display:block; margin-top:10px; margin-bottom:2px; }
  .sec:first-child { margin-top:0; }
  .warning { background:#fffbeb; color:#92400e; border:1.5px solid #fde68a; border-radius:12px; padding:11px 13px; font-size:12px; text-align:center; line-height:1.6; margin-bottom:18px; }
  .alarm-box { background:linear-gradient(135deg,#eff6ff,#f0fdf4); border:2px dashed #93c5fd; border-radius:18px; padding:18px; }
  .alarm-box h4 { font-size:15px; font-weight:800; color:#1e40af; margin-bottom:14px; text-align:center; }.alarm-row { display:flex; gap:8px; align-items:center; margin-bottom:10px; }
  .alarm-row input[type="time"] { flex:1; padding:11px 13px; border:2px solid #bfdbfe; border-radius:10px; font-size:15px; font-family:'Nunito',sans-serif; outline:none; color:#1e3a8a; transition:border .2s; }
  .btn-save { padding:11px 16px; background:linear-gradient(135deg,var(--green),#34d399); color:white; border:none; border-radius:10px; font-size:13px; font-weight:800; cursor:pointer; font-family:'Nunito',sans-serif; white-space:nowrap; }
  .daily-row { display:flex; align-items:center; gap:10px; margin-bottom:12px; font-size:13.5px; font-weight:700; color:#1e40af; }
  .toggle { position:relative; width:44px; height:24px; display:inline-block; flex-shrink:0; }
  .toggle input { opacity:0; width:0; height:0; }
  .slider { position:absolute; cursor:pointer; inset:0; background:#cbd5e1; border-radius:24px; transition:.3s; }
  .slider:before { content:''; position:absolute; width:18px; height:18px; left:3px; bottom:3px; background:white; border-radius:50%; transition:.3s; }
  .toggle input:checked + .slider { background:var(--blue); }
  .toggle input:checked + .slider:before { transform:translateX(20px); }
  #alarm-list { margin-top:4px; }
  .alarm-item { display:flex; align-items:center; justify-content:space-between; background:white; border:1.5px solid #bfdbfe; border-radius:10px; padding:9px 12px; margin-bottom:6px; font-size:13px; }
  .alarm-item .atime { font-weight:800; color:#1e40af; }
  .alarm-item .badge { font-size:11px; font-weight:700; padding:2px 8px; border-radius:6px; background:#dbeafe; color:#1e40af; }
  .alarm-item .badge.daily { background:#d1fae5; color:#065f46; }
  .alarm-del { background:none; border:none; cursor:pointer; font-size:16px; color:#ef4444; line-height:1; padding:0 2px; }
  .no-alarm { text-align:center; color:#94a3b8; font-size:13px; padding:6px 0; }
  .spinner { display:inline-block; width:16px; height:16px; border:3px solid #bfdbfe; border-top-color:var(--blue); border-radius:50%; animation:spin .7s linear infinite; vertical-align:middle; margin-right:8px; }
  @keyframes spin { to{transform:rotate(360deg)} }
  #toast { position:fixed; bottom:28px; left:50%; transform:translateX(-50%) translateY(80px); background:#1e293b; color:white; padding:12px 22px; border-radius:14px; font-size:14px; font-weight:700; box-shadow:0 6px 24px rgba(0,0,0,0.25); z-index:999; opacity:0; transition:all .35s cubic-bezier(.34,1.56,.64,1); pointer-events:none; white-space:nowrap; }
  #toast.show { opacity:1; transform:translateX(-50%) translateY(0); }
  .footer { text-align:center; font-size:11px; color:#94a3b8; margin-top:16px; }
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>🛡️ MedAssist Pro</h1>
    <p>AI yordamida dori ma'lumotlari • 3 tilda</p>
  </div>
  <div class="body">
    <div class="search-row">
      <input type="text" id="drug-input" placeholder="Dori nomi... (masalan: Paracetamol)" onkeydown="if(event.key==='Enter') ask()">
      <button class="btn-go" id="btn-search" onclick="ask()">🔍</button>
    </div>
    <div class="lang-group">
      <button class="btn-lang uz active" id="btn-uz" onclick="setL('uz')">🇺🇿 O'ZBEK</button>
      <button class="btn-lang ru" id="btn-ru" onclick="setL('ru')">🇷🇺 РУССКИЙ</button>
      <button class="btn-lang en" id="btn-en" onclick="setL('en')">🇺🇸 ENGLISH</button>
    </div>
    <div id="result-box" class="result">💊 Dori nomini kiriting va qidiring...</div>
    <div class="warning">
      ⚠️ <strong>DIQQAT:</strong> Ma'lumotlar AI tomonidan berilgan.
      Dorini ichishdan oldin albatta <strong>shifokor bilan maslahatlashing!</strong>
    </div>
    <div class="alarm-box">
      <h4>⏰ Dori ichish eslatmasi</h4>
      <div class="alarm-row">
        <input type="time" id="alarm-time"><button class="btn-save" onclick="addAlarm()">➕ Qo'shish</button>
      </div>
      <div class="daily-row">
        <label class="toggle">
          <input type="checkbox" id="daily-toggle" checked>
          <span class="slider"></span>
        </label>
        <span>Har kuni takrorlansin</span>
      </div>
      <div id="alarm-list"></div>
    </div>
  </div>
  <div class="footer">MedAssist Pro • Faqat ma'lumot uchun • © 2025</div>
</div>
<div id="toast"></div>

<script>
let currentLang = 'uz';
function setL(lang) {
  currentLang = lang;
  ['uz','ru','en'].forEach(l => document.getElementById('btn-'+l).classList.toggle('active', l===lang));
}

async function ask() {
  const name = document.getElementById('drug-input').value.trim();
  if (!name) { toast('⚠️ Dori nomini kiriting'); return; }
  const box = document.getElementById('result-box');
  const btn = document.getElementById('btn-search');
  box.innerHTML = '<span class="spinner"></span> Qidirilmoqda...';
  btn.disabled = true;
  try {
    const res = await fetch('/get_drug', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name: name, lang: currentLang})
    });
    const data = await res.json();
    if (!res.ok) { box.innerHTML = '❌ Xato: ' + (data.error || 'Server xatosi'); return; }
    box.innerHTML = data.text
      .replace(/TARKIBI:/gi, '<span class="sec">🧪 TARKIBI:</span>')
      .replace(/DOZASI:/gi,  '<span class="sec">⚖️ DOZASI:</span>')
      .replace(/FOYDASI:/gi, '<span class="sec">✅ FOYDASI:</span>')
      .replace(/ZARARI:/gi,  '<span class="sec">❌ ZARARI:</span>')
      .split('\\n').join('<br>');
  } catch(e) {
    box.innerHTML = '❌ Ulanish xatosi: ' + e.message;
  } finally {
    btn.disabled = false;
  }
}

function getAlarms() { try { return JSON.parse(localStorage.getItem('med_alarms')||'[]'); } catch{return[];} }
function saveAlarms(a) { localStorage.setItem('med_alarms', JSON.stringify(a)); }

function addAlarm() {
  const t = document.getElementById('alarm-time').value;
  if (!t) { toast('⚠️ Vaqtni tanlang'); return; }
  const daily = document.getElementById('daily-toggle').checked;
  const alarms = getAlarms();
  if (alarms.find(a=>a.time===t)) { toast('⚠️ Bu vaqt allaqachon bor'); return; }
  alarms.push({time:t, daily:daily});
  saveAlarms(alarms); renderAlarms();
  document.getElementById('alarm-time').value = '';
  toast('🔔 ' + t + (daily?' • Har kuni':' • Bir marta'));
  if (Notification.permission==='default') Notification.requestPermission();
}

function deleteAlarm(time) {
  saveAlarms(getAlarms().filter(a=>a.time!==time));
  renderAlarms(); toast('🗑️ O\'chirildi: '+time);
}

function renderAlarms() {
  const alarms = getAlarms();
  const list = document.getElementById('alarm-list');
  if (!alarms.length) { list.innerHTML='<p class="no-alarm">Hozircha eslatma yo\'q</p>'; return; }
  list.innerHTML = alarms.map(a=>
    <div class="alarm-item">
      <span class="atime">⏰ ${a.time}</span>
      <span class="badge ${a.daily?'daily':''}">${a.daily?'🔁 Har kuni':'1️⃣ Bir marta'}</span>
      <button class="alarm-del" onclick="deleteAlarm('${a.time}')">🗑️</button>
    </div>).join('');
}

function todayStr() { const d=new Date(); return d.getFullYear()+'-'+d.getMonth()+'-'+d.getDate(); }
function getFired() { try{return JSON.parse(localStorage.getItem('med_fired')||'{}');}catch{return{};} }
function markFired(t) {
  const fd=getFired(), td=todayStr();
  if(!fd[td]) fd[td]=[];
  if(!fd[td].includes(t)) fd[td].push(t);
  const keys=Object.keys(fd); if(keys.length>3) delete fd[keys[0]];
  localStorage.setItem('med_fired', JSON.stringify(fd));
}
function hasFiredToday(t) { return (getFired()[todayStr()]||[]).includes(t); }

setInterval(()=>{
  const alarms=getAlarms(); if(!alarms.length) return;const now=new Date();
  const cur=now.getHours().toString().padStart(2,'0')+':'+now.getMinutes().toString().padStart(2,'0');
  alarms.forEach(a=>{
    if(a.time!==cur || hasFiredToday(a.time)) return;
    markFired(a.time);
    alert('🚨 VAQT BO\'LDI! DORINGIZNI ICHING!\\n⏰ '+cur+'\\n(Shifokor tavsiyasiga amal qiling)');
    if(Notification.permission==='granted') new Notification('🛡️ MedAssist Pro',{body:'⏰ '+cur+' — Dori ichish vaqti keldi!'});
    if(!a.daily){ saveAlarms(getAlarms().filter(x=>x.time!==a.time)); renderAlarms(); }
  });
}, 15000);

function toast(msg) {
  const el=document.getElementById('toast');
  el.textContent=msg; el.classList.add('show');
  setTimeout(()=>el.classList.remove('show'),3000);
}
window.onload = ()=>{ renderAlarms(); };
</script>
</body>
</html>"""


@app.route('/')
def home():
    logger.info("Sahifa ochildi")
    return HTML_PAGE


@app.route('/get_drug', methods=['POST'])
def get_drug():
    try:
        data = request.json
        drug_name = data.get('name', '').strip()
        lang = data.get('lang', 'uz').strip()

        if not drug_name:
            return jsonify({"error": "Dori nomi bo'sh"}), 400

        lang_map = {'uz': "o'zbek", 'ru': "rus", 'en': "ingliz"}
        lang_name = lang_map.get(lang, "o'zbek")

        logger.info(f"Qidirish: '{drug_name}' | til: {lang}")

        prompt = (
            f'"{drug_name}" dorisi haqida {lang_name} tilida aniq ma\'lumot ber.\n'
            f'Faqat quyidagi 4 bo\'lim bilan yoz:\n'
            f'TARKIBI: (kimyoviy tarkibi)\n'
            f'DOZASI: (standart doza)\n'
            f'FOYDASI: (asosiy qo\'llanilishi)\n'
            f'ZARARI: (yon ta\'sirlar)'
        )

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = message.content[0].text
        logger.info(f"Javob berildi: '{drug_name}'")
        return jsonify({"text": answer})

    except anthropic.AuthenticationError:
        logger.error("API kalit noto'g'ri!")
        return jsonify({"error": "API kalit noto'g'ri"}), 401
    except anthropic.RateLimitError:
        logger.error("API limit tugadi")
        return jsonify({"error": "API limiti tugadi, keyinroq urinib ko'ring"}), 429
    except Exception as e:
        logger.error(f"Xato: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info("MedAssist Pro ishga tushdi")
    app.run(host='0.0.0.0', port=10000, debug=False)
