import os
from flask import Flask, render_template_string, request, jsonify
import pymysql
import google.generativeai as genai

app = Flask(__name__)

# --- 1. إعداد ذكاء Gemini بمفتاحك الخاص ---
GEMINI_API_KEY = "AIzaSyBloSG8gV9tf5fP3NNICuoeKzpMpAbE2H8"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. إعدادات قاعدة بيانات Aiven ---
DB_CONFIG = {
    'host': 'mysql-colab-oliver59oliv-1ac2.f.aivencloud.com',
    'port': 23043,
    'user': 'avnadmin',
    'password': 'AVNS__uZT75lw-GrX9bxvmF1',
    'database': 'defaultdb',
}

# --- 3. واجهة المستخدم الاحترافية ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Oliver Smart AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 95%; max-width: 450px; height: 600px; background: #161b22; border-radius: 20px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #30363d; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .header { background: #21262d; padding: 15px; text-align: center; font-weight: bold; color: #58a6ff; border-bottom: 1px solid #30363d; }
        #chat-window { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; scroll-behavior: smooth; }
        .bubble { padding: 10px 15px; border-radius: 15px; max-width: 80%; font-size: 14px; line-height: 1.4; position: relative; }
        .user { align-self: flex-start; background: #238636; color: white; border-bottom-right-radius: 2px; }
        .ai { align-self: flex-end; background: #30363d; color: #c9d1d9; border-bottom-left-radius: 2px; border: 1px solid #444; }
        .input-area { padding: 15px; background: #161b22; display: flex; gap: 8px; border-top: 1px solid #30363d; }
        input { flex: 1; padding: 12px; border-radius: 10px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; }
        button { background: #1f6feb; color: white; border: none; padding: 0 15px; border-radius: 10px; cursor: pointer; }
        .loading { font-size: 12px; color: #8b949e; margin-right: 10px; display: none; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">🤖 مساعد أوليفير الذكي</div>
        <div id="chat-window"></div>
        <div id="loading-text" class="loading">جاري التفكير...</div>
        <div class="input-area">
            <input type="text" id="msg-input" placeholder="اسألني أي شيء...">
            <button onclick="send()">إرسال</button>
        </div>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('msg-input');
            const windowDiv = document.getElementById('chat-window');
            const loader = document.getElementById('loading-text');
            const text = input.value.trim();
            if(!text) return;

            windowDiv.innerHTML += `<div class="bubble user">${text}</div>`;
            input.value = '';
            windowDiv.scrollTop = windowDiv.scrollHeight;
            loader.style.display = 'block';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                loader.style.display = 'none';
                windowDiv.innerHTML += `<div class="bubble ai">${data.reply}</div>`;
                windowDiv.scrollTop = windowDiv.scrollHeight;
            } catch(e) {
                loader.style.display = 'none';
                windowDiv.innerHTML += `<div class="bubble ai" style="color:#f85149">⚠️ خطأ في الاتصال!</div>`;
            }
        }
        document.getElementById('msg-input').addEventListener("keypress", (e) => { if(e.key === "Enter") send(); });
    </script>
</body>
</html>
"""

# --- 4. منطق السيرفر والذكاء الاصطناعي ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    try:
        # استدعاء Gemini للرد
        ai_response = model.generate_content(user_msg)
        reply_text = ai_response.text

        # حفظ المحادثة في MySQL
        conn = pymysql.connect(**DB_CONFIG, ssl={'ssl': True})
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_text TEXT,
                    ai_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("INSERT INTO memory_log (user_text, ai_text) VALUES (%s, %s)", (user_msg, reply_text))
            conn.commit()
        conn.close()

        return jsonify({"reply": reply_text})
    except Exception as e:
        return jsonify({"reply": f"عذراً أوليفير، حدث خطأ: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)