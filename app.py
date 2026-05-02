import logging
import json
import os
from flask import Flask, request, jsonify
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)

HTML_PAGE = (
    "<!DOCTYPE html>"
    "<html lang='uz'>"
    "<head>"
    "<meta charset='UTF-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    "<title>MedAssist Pro</title>"
    "<link href='https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap' rel='stylesheet'>"
    "<style>"
    ":root{--blue:#0062cc;--blue2:#00b4d8;--green:#059669;--red:#dc2626;--yellow:#d97706;--bg:#eef6ff;--card:#fff;--text:#1e293b;--muted:#64748b;--border:#e2e8f0}"
    "*{box-sizing:border-box;margin:0;padding:0}"
    "body{font-family:'Nunito',sans-serif;background:var(--bg);min-height:100vh;padding:20px 14px 50px}"
    ".card{background:var(--card);max-width:540px;margin:0 auto;border-radius:24px;box-shadow:0 8px 40px rgba(0,98,204,0.13);overflow:hidden}"
    ".header{background:linear-gradient(135deg,var(--blue),var(--blue2));color:white;padding:24px 20px;text-align:center}"
    ".header h1{font-size:24px;font-weight:900}"
    ".header p{font-size:12.5px;opacity:.85;margin-top:5px}"
    ".body{padding:22px 18px}"
    ".search-row{display:flex;gap:8px;margin-bottom:12px}"
    ".search-row input{flex:1;padding:13px 15px;border:2px solid var(--border);border-radius:12px;font-size:15px;font-family:'Nunito',sans-serif;outline:none;transition:border .2s;color:var(--text)}"
    ".search-row input:focus{border-color:var(--blue)}"
    ".search-row input::placeholder{color:#a0aec0}"
    ".btn-go{padding:13px 18px;background:linear-gradient(135deg,var(--blue),var(--blue2));color:white;border:none;border-radius:12px;font-size:15px;font-weight:800;cursor:pointer;font-family:'Nunito',sans-serif}"
    ".btn-go:disabled{opacity:.5;cursor:not-allowed}"
    ".lang-group{display:flex;gap:7px;margin-bottom:16px}"
    ".btn-lang{flex:1;padding:10px 5px;border:2.5px solid transparent;border-radius:10px;font-size:12.5px;font-weight:800;cursor:pointer;font-family:'Nunito',sans-serif}"
    ".btn-lang.uz{background:#d1fae5;color:#065f46;border-color:#6ee7b7}"
    ".btn-lang.ru{background:#fef3c7;color:#92400e;border-color:#fcd34d}"
    ".btn-lang.en{background:#fee2e2;color:#991b1b;border-color:#fca5a5}"
    ".btn-lang.uz.active{background:var(--green);color:white;border-color:var(--green)}"
    ".btn-lang.ru.active{background:var(--yellow);color:white;border-color:var(--yellow)}"
    ".btn-lang.en.active{background:var(--red);color:white;border-color:var(--red)}"
    "#result-box{margin-bottom:16px}"
    ".placeholder{background:#f8faff;border:1.5px solid var(--border);border-left:5px solid var(--blue);border-radius:14px;padding:20px;font-size:14px;color:var(--muted);text-align:center}"
    ".section-card{border-radius:14px;padding:14px 16px;margin-bottom:10px;border-left:5px solid}"
    ".section-card.tarkibi{background:#eff6ff;border-color:#3b82f6}"
    ".section-card.dozasi{background:#f0fdf4;border-color:#22c55e}"
    ".section-card.foydasi{background:#fefce8;border-color:#eab308}"
    ".section-card.zarari{background:#fff1f2;border-color:#f43f5e}"
    ".section-title{font-size:13px;font-weight:900;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}"
    ".section-card.tarkibi .section-title{color:#1d4ed8}"
    ".section-card.dozasi .section-title{color:#15803d}"
    ".section-card.foydasi .section-title{color:#a16207}"
    ".section-card.zarari .section-title{color:#be123c}"
    ".section-body{font-size:14px;line-height:1.75;color:var(--text)}"
    ".loading-box{background:#f8faff;border:1.5px solid var(--border);border-radius:14px;padding:24px;text-align:center;color:var(--muted);font-size:14px}"".spinner{display:inline-block;width:20px;height:20px;border:3px solid #bfdbfe;border-top-color:var(--blue);border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:8px}"
    "@keyframes spin{to{transform:rotate(360deg)}}"
    ".warning{background:#fffbeb;color:#92400e;border:1.5px solid #fde68a;border-radius:12px;padding:11px 14px;font-size:12px;text-align:center;line-height:1.6;margin-bottom:18px}"
    ".alarm-box{background:linear-gradient(135deg,#eff6ff,#f0fdf4);border:2px dashed #93c5fd;border-radius:18px;padding:18px}"
    ".alarm-box h4{font-size:15px;font-weight:900;color:#1e40af;margin-bottom:14px;text-align:center}"
    ".alarm-row{display:flex;gap:8px;align-items:center;margin-bottom:10px}"
    ".alarm-row input[type=time]{flex:1;padding:11px 13px;border:2px solid #bfdbfe;border-radius:10px;font-size:15px;font-family:'Nunito',sans-serif;outline:none;color:#1e3a8a}"
    ".btn-save{padding:11px 16px;background:linear-gradient(135deg,var(--green),#34d399);color:white;border:none;border-radius:10px;font-size:13px;font-weight:800;cursor:pointer;font-family:'Nunito',sans-serif;white-space:nowrap}"
    ".daily-row{display:flex;align-items:center;gap:10px;margin-bottom:12px;font-size:13.5px;font-weight:700;color:#1e40af}"
    ".toggle{position:relative;width:44px;height:24px;display:inline-block;flex-shrink:0}"
    ".toggle input{opacity:0;width:0;height:0}"
    ".slider{position:absolute;cursor:pointer;inset:0;background:#cbd5e1;border-radius:24px;transition:.3s}"
    ".slider:before{content:'';position:absolute;width:18px;height:18px;left:3px;bottom:3px;background:white;border-radius:50%;transition:.3s}"
    ".toggle input:checked + .slider{background:var(--blue)}"
    ".toggle input:checked + .slider:before{transform:translateX(20px)}"
    "#alarm-list{margin-top:6px}"
    ".alarm-item{display:flex;align-items:center;justify-content:space-between;background:white;border:1.5px solid #bfdbfe;border-radius:10px;padding:9px 12px;margin-bottom:6px;font-size:13px}"
    ".alarm-item .atime{font-weight:800;color:#1e40af}"
    ".alarm-item .badge{font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;background:#dbeafe;color:#1e40af}"
    ".alarm-item .badge.daily{background:#d1fae5;color:#065f46}"
    ".alarm-del{background:none;border:none;cursor:pointer;font-size:16px;color:#ef4444}"
    ".no-alarm{text-align:center;color:#94a3b8;font-size:13px;padding:6px 0}"
    "#toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(80px);background:#1e293b;color:white;padding:12px 22px;border-radius:14px;font-size:14px;font-weight:700;box-shadow:0 6px 24px rgba(0,0,0,0.25);z-index:999;opacity:0;transition:all .35s;pointer-events:none;white-space:nowrap}"
    "#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}"
    ".footer{text-align:center;font-size:11px;color:#94a3b8;margin-top:16px}"
    "</style>"
    "</head>"
    "<body>"
    "<div class='card'>"
    "<div class='header'><h1>MedAssist Pro</h1><p>AI yordamida dori malumotlari - 3 tilda</p></div>"
    "<div class='body'>"
    "<div class='search-row'>"
    "<input type='text' id='drug-input' placeholder='Dori nomi... (masalan: Paracetamol)'>"
    "<button class='btn-go' id='btn-search'>Qidirish</button>"
    "</div>"
    "<div class='lang-group'>"
    "<button class='btn-lang uz active' id='btn-uz'>UZBEK</button>"
    "<button class='btn-lang ru' id='btn-ru'>RUSSIAN</button>"
    "<button class='btn-lang en' id='btn-en'>ENGLISH</button>"
    "</div>"
    "<div id='result-box'><div class='placeholder'>Dori nomini kiriting va qidiring...</div></div>"
    "<div class='warning'>DIQQAT: Malumotlar AI tomonidan berilgan. Dorini ichishdan oldin albatta shifokor bilan maslahatlashing!</div>"
    "<div class='alarm-box'>""<h4>Dori ichish eslatmasi</h4>"
    "<div class='alarm-row'><input type='time' id='alarm-time'><button class='btn-save' id='btn-add'>Qoshish</button></div>"
    "<div class='daily-row'><label class='toggle'><input type='checkbox' id='daily-toggle' checked><span class='slider'></span></label><span>Har kuni takrorlansin</span></div>"
    "<div id='alarm-list'></div>"
    "</div>"
    "</div>"
    "<div class='footer'>MedAssist Pro - Faqat malumot uchun - 2025</div>"
    "</div>"
    "<div id='toast'></div>"
    "<script>"
    "var lang='uz';"
    "document.getElementById('btn-uz').onclick=function(){lang='uz';setActive('btn-uz');};"
    "document.getElementById('btn-ru').onclick=function(){lang='ru';setActive('btn-ru');};"
    "document.getElementById('btn-en').onclick=function(){lang='en';setActive('btn-en');};"
    "function setActive(id){['btn-uz','btn-ru','btn-en'].forEach(function(b){document.getElementById(b).classList.remove('active');});document.getElementById(id).classList.add('active');}"
    "document.getElementById('btn-search').onclick=function(){search();};"
    "document.getElementById('drug-input').onkeydown=function(e){if(e.key==='Enter')search();};"
    "function search(){"
    "var name=document.getElementById('drug-input').value.trim();"
    "if(!name){toast('Dori nomini kiriting');return;}"
    "var box=document.getElementById('result-box');"
    "var btn=document.getElementById('btn-search');"
    "btn.disabled=true;"
    "box.innerHTML='<div class=\\'loading-box\\'><span class=\\'spinner\\'></span>Qidirilmoqda...</div>';"
    "fetch('/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,lang:lang})})"
    ".then(function(r){return r.json();})"
    ".then(function(d){"
    "btn.disabled=false;"
    "if(d.error){box.innerHTML='<div class=\\'placeholder\\'>Xato: '+d.error+'</div>';return;}"
    "var h='';"
    "if(d.tarkibi)h+='<div class=\\'section-card tarkibi\\'><div class=\\'section-title\\'>Tarkibi</div><div class=\\'section-body\\'>'+d.tarkibi+'</div></div>';"
    "if(d.dozasi)h+='<div class=\\'section-card dozasi\\'><div class=\\'section-title\\'>Dozasi va Qollanilishi</div><div class=\\'section-body\\'>'+d.dozasi+'</div></div>';"
    "if(d.foydasi)h+='<div class=\\'section-card foydasi\\'><div class=\\'section-title\\'>Foydasi</div><div class=\\'section-body\\'>'+d.foydasi+'</div></div>';"
    "if(d.zarari)h+='<div class=\\'section-card zarari\\'><div class=\\'section-title\\'>Zarari</div><div class=\\'section-body\\'>'+d.zarari+'</div></div>';"
    "if(!h)h='<div class=\\'placeholder\\'>Malumot topilmadi</div>';"
    "box.innerHTML=h;"
    "})"
    ".catch(function(e){btn.disabled=false;box.innerHTML='<div class=\\'placeholder\\'>Xato: '+e.message+'</div>';});"
    "}"
    "function getAlarms(){try{return JSON.parse(localStorage.getItem('med_alarms')||'[]');}catch(e){return[];}}"
    "function saveAlarms(a){localStorage.setItem('med_alarms',JSON.stringify(a));}"
    "document.getElementById('btn-add').onclick=function(){"
    "var t=document.getElementById('alarm-time').value;"
    "if(!t){toast('Vaqtni tanlang');return;}"
    "var daily=document.getElementById('daily-toggle').checked;"
    "var alarms=getAlarms();"
    "for(var i=0;i<alarms.length;i++){if(alarms[i].time===t){toast('Bu vaqt allaqachon bor');return;}}"
    "alarms.push({time:t,daily:daily});"
    "saveAlarms(alarms);renderAlarms();"
    "document.getElementById('alarm-time').value='';"
    "toast('Eslatma saqlandi: '+t);"
    "if(Notification.permission==='default')Notification.requestPermission();"
    "};"
    "function delAlarm(t){saveAlarms(getAlarms().filter(function(a){return a.time!==t;}));renderAlarms();toast('Ochirildi: '+t);}"
    "function renderAlarms(){"
    "var alarms=getAlarms();""var list=document.getElementById('alarm-list');"
    "if(!alarms.length){list.innerHTML='<p class=\\'no-alarm\\'>Hozircha eslatma yoq</p>';return;}"
    "var h='';"
    "for(var i=0;i<alarms.length;i++){"
    "h+='<div class=\\'alarm-item\\'>';"
    "h+='<span class=\\'atime\\'>'+alarms[i].time+'</span>';"
    "h+='<span class=\\'badge '+(alarms[i].daily?'daily':'')+'\\'>'+(alarms[i].daily?'Har kuni':'Bir marta')+'</span>';"
    "h+='<button class=\\'alarm-del\\' onclick=\\'delAlarm(\\\"'+alarms[i].time+'\\\")\\'>X</button>';"
    "h+='</div>';"
    "}"
    "list.innerHTML=h;"
    "}"
    "function todayStr(){var d=new Date();return d.getFullYear()+'-'+d.getMonth()+'-'+d.getDate();}"
    "function getFired(){try{return JSON.parse(localStorage.getItem('med_fired')||'{}');}catch(e){return{};}}"
    "function markFired(t){var fd=getFired(),td=todayStr();if(!fd[td])fd[td]=[];if(fd[td].indexOf(t)===-1)fd[td].push(t);localStorage.setItem('med_fired',JSON.stringify(fd));}"
    "function hasFired(t){var fd=getFired(),td=todayStr();return fd[td]&&fd[td].indexOf(t)!==-1;}"
    "setInterval(function(){"
    "var alarms=getAlarms();if(!alarms.length)return;"
    "var now=new Date();"
    "var h=now.getHours().toString().padStart(2,'0');"
    "var m=now.getMinutes().toString().padStart(2,'0');"
    "var cur=h+':'+m;"
    "for(var i=0;i<alarms.length;i++){"
    "if(alarms[i].time!==cur||hasFired(alarms[i].time))continue;"
    "markFired(alarms[i].time);"
    "alert('VAQT BOLDI! DORINGIZNI ICHING! Vaqt: '+cur);"
    "if(Notification.permission==='granted')new Notification('MedAssist Pro',{body:cur+' - Dori ichish vaqti!'});"
    "if(!alarms[i].daily)delAlarm(alarms[i].time);"
    "}"
    "},15000);"
    "function toast(msg){var el=document.getElementById('toast');el.textContent=msg;el.classList.add('show');setTimeout(function(){el.classList.remove('show');},3000);}"
    "window.onload=function(){renderAlarms();};"
    "</script>"
    "</body></html>"
)


@app.route('/')
def home():
    logger.info("Sahifa ochildi")
    return HTML_PAGE


@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        drug_name = data.get('name', '').strip()
        lang = data.get('lang', 'uz').strip()

        if not drug_name:
            return jsonify({"error": "Dori nomi bosh"}), 400

        lang_map = {'uz': "o'zbek", 'ru': "rus", 'en': "ingliz"}
        lang_name = lang_map.get(lang, "o'zbek")

        logger.info("Qidirish: %s | til: %s", drug_name, lang)

        prompt = (
            'Sen tibbiy yordamchisan. '
            + '"' + drug_name + '"'
            + ' dorisi haqida ' + lang_name + ' tilida malumot ber. '
            + 'Javobni faqat JSON formatda ber, boshqa hech narsa yozma. '
            + 'Format: {"tarkibi":"...","dozasi":"...","foydasi":"...","zarari":"..."}'
        )

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            llama-3.3-70b-versatile
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()
        logger.info("Javob: %s", raw)

        start = raw.find('{')
        end = raw.rfind('}')
        if start == -1 or end == -1:
            raise ValueError("JSON topilmadi")

        result = json.loads(raw[start:end+1])
        for key in result:
            result[key] = result[key].replace('\n', '<br>')

        logger.info("Muvaffaqiyat: %s", drug_name)
        return jsonify(result)

    except Exception as e:
        logger.error("Xato: %s", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info("MedAssist Pro ishga tushdi")
    app.run(host='0.0.0.0', port=10000, debug=False)
