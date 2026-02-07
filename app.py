import os
from flask import Flask, render_template_string, request, jsonify
import pymysql
import google.generativeai as genai

app = Flask(__name__)

# --- 1. إعداد ذكاء Gemini ---
GEMINI_API_KEY = "AIzaSyBloSG8gV9tf5fP3NNICuoeKzpMpAbE2H8"
genai.configure(api_key=GEMINI_API_KEY)

# محاولة استخدام الموديل المستقر
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. إعدادات قاعدة بيانات Aiven ---
DB_CONFIG = {
    'host': 'mysql-colab-oliver59oliv-1ac2.f.aivencloud.com',
    'port': 23043,
    'user': 'avnadmin',
    'password': 'AVNS__uZT75lw-GrX9bxvmF1',
    'database': 'defaultdb',
}

# --- 3. واجهة المستخدم ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Oliver AI | Stable</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 95%; max-width: 420px; height: 80vh; background: #161b22; border-radius: 20px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #30363d; }
        .header { background: #21262d; padding: 15px; text-align: center; color: #58a6ff; font-weight: bold; border-bottom: 1px solid #30363d; }
        #chat-window { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .bubble { padding: 10px 15px; border-radius: 15px; max-width: 80%; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
        .user { align-self: flex-start; background: #238636; color: white; }
        .ai { align-self: flex-end; background: #30363d; color: #c9d1d9; border: 1px solid #444; }
        .input-area { padding: 15px; background: #161b22; display: flex; gap: 8px; border-top: 1px solid #30363d; }
        input { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; }
        button { background: #1f6feb; color: white; border: none; padding: 0 15px; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">🤖 مساعد أوليفير الذكي</div>
        <div id="chat-window"></div>
        <div class="input-area">
            <input type="text" id="msg-input" placeholder="اسألني أي شيء...">
            <button onclick="send()">إرسال</button>
        </div>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('msg-input');
            const windowDiv = document.getElementById('chat-window');
            if(!input.value.trim()) return;

            const text = input.value;
            windowDiv.innerHTML += `<div class="bubble user">${text}</div>`;
            input.value = '';
            windowDiv.scrollTop = windowDiv.scrollHeight;

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            windowDiv.innerHTML += `<div class="bubble ai">${data.reply}</div>`;
            windowDiv.scrollTop = windowDiv.scrollHeight;
        }
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
        # استدعاء الرد
        response = model.generate_content(user_msg)
        reply_text = response.text

        # حفظ في القاعدة
        try:
            conn = pymysql.connect(**DB_CONFIG, ssl={'ssl': True})
            with conn.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS chat_log (id INT AUTO_INCREMENT PRIMARY KEY, u TEXT, a TEXT)")
                cursor.execute("INSERT INTO chat_log (u, a) VALUES (%s, %s)", (user_msg, reply_text))
                conn.commit()
            conn.close()
        except: pass # إذا فشلت القاعدة لا نعطل الرد

        return jsonify({"reply": reply_text})
    
    except Exception as e:
        # إذا فشل الفلاش، سنحاول تجربة الموديل البديل تلقائياً
        try:
            alt_model = genai.GenerativeModel('gemini-pro')
            response = alt_model.generate_content(user_msg)
            return jsonify({"reply": response.text})
        except:
            return jsonify({"reply": f"خطأ في الموديل: {str(e)}. تأكد من تفعيل Gemini API في Google Cloud."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))