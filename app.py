import os
from flask import Flask, render_template_string, request, jsonify
import pymysql
import google.generativeai as genai

app = Flask(__name__)

# --- 1. إعداد ذكاء Gemini (المجاني) ---
GEMINI_API_KEY = "AIzaSyBloSG8gV9tf5fP3NNICuoeKzpMpAbE2H8"
genai.configure(api_key=GEMINI_API_KEY)

# استخدام الإصدار المستقر والأكثر توافقاً
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. إعدادات قاعدة بيانات Aiven ---
DB_CONFIG = {
    'host': 'mysql-colab-oliver59oliv-1ac2.f.aivencloud.com',
    'port': 23043,
    'user': 'avnadmin',
    'password': 'AVNS__uZT75lw-GrX9bxvmF1',
    'database': 'defaultdb',
}

# --- 3. واجهة المستخدم (تصميم أنيق وملموم) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Oliver AI | Free Edition</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0d1117; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 95%; max-width: 420px; height: 85vh; background: #161b22; border-radius: 24px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #30363d; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }
        .header { background: #21262d; padding: 18px; text-align: center; font-weight: bold; color: #58a6ff; border-bottom: 1px solid #30363d; font-size: 18px; }
        #chat-window { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }
        .bubble { padding: 12px 16px; border-radius: 18px; max-width: 85%; font-size: 15px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
        .user { align-self: flex-start; background: #238636; color: white; border-bottom-right-radius: 4px; }
        .ai { align-self: flex-end; background: #30363d; color: #c9d1d9; border-bottom-left-radius: 4px; border: 1px solid #444; }
        .input-area { padding: 15px; background: #161b22; display: flex; gap: 10px; border-top: 1px solid #30363d; }
        input { flex: 1; padding: 12px 15px; border-radius: 12px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; transition: 0.3s; }
        input:focus { border-color: #58a6ff; }
        button { background: #1f6feb; color: white; border: none; padding: 0 20px; border-radius: 12px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #388bfd; }
        #status { font-size: 12px; text-align: center; color: #8b949e; padding: 5px; min-height: 20px; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">✨ ذكاء أوليفير المجاني</div>
        <div id="chat-window"></div>
        <div id="status"></div>
        <div class="input-area">
            <input type="text" id="msg-input" placeholder="اسألني أي شيء..." autocomplete="off">
            <button onclick="send()">إرسال</button>
        </div>
    </div>
    <script>
        const chatWindow = document.getElementById('chat-window');
        const status = document.getElementById('status');
        const input = document.getElementById('msg-input');

        async function send() {
            const text = input.value.trim();
            if(!text) return;

            // رسالة المستخدم
            chatWindow.innerHTML += `<div class="bubble user">${text}</div>`;
            input.value = '';
            chatWindow.scrollTop = chatWindow.scrollHeight;
            status.innerText = "جاري التفكير...";

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                status.innerText = "";
                
                // رسالة الـ AI
                chatWindow.innerHTML += `<div class="bubble ai">${data.reply}</div>`;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            } catch(e) {
                status.innerText = "⚠️ فشل الاتصال";
            }
        }
        input.addEventListener("keypress", (e) => { if(e.key === "Enter") send(); });
    </script>
</body>
</html>
"""

# --- 4. منطق السيرفر ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    try:
        # 1. الحصول على الرد من Gemini
        response = model.generate_content(user_msg)
        reply_text = response.text

        # 2. الحفظ في قاعدة بيانات Aiven
        conn = pymysql.connect(**DB_CONFIG, ssl={'ssl': True})
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_memory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_msg TEXT,
                    ai_reply TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("INSERT INTO chat_memory (user_msg, ai_reply) VALUES (%s, %s)", (user_msg, reply_text))
            conn.commit()
        conn.close()

        return jsonify({"reply": reply_text})
    except Exception as e:
        return jsonify({"reply": f"حدث خطأ بسيط: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))