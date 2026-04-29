import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq # openai o'rniga groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ... (home route qismi o'zgarishsiz qoladi)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    dori_nomi = data.get('dori')
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192", # Juda tezkor bepul model
            messages=[{"role": "user", "content": f"{dori_nomi} dorisi haqida o'zbek tilida ma'lumot ber."}]
        )
        return jsonify({'result': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'result': "Xatolik: " + str(e)})

if __name__ == '__main__':
    app.run(debug=True)
