import os
from flask import Flask, render_template_string, request, jsonify
import pymysql

app = Flask(__name__)

# بيانات الاتصال (تأكد من صحتها)
DB_CONFIG = {
    'host': 'mysql-colab-oliver59oliv-1ac2.f.aivencloud.com',
    'port': 23043,
    'user': 'avnadmin',
    'password': 'AVNS__uZT75lw-GrX9bxvmF1',
    'database': 'defaultdb',
}

# واجهة المستخدم الاحترافية
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Oliver Personal AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background: #252525; padding: 20px; text-align: center; border-bottom: 2px solid #007bff; font-size: 1.2em; }
        #chat-window { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
        .bubble { padding: 12px 18px; border-radius: 15px; max-width: 75%; word-wrap: break-word; }
        .user { align-self: flex-start; background: #007bff; }
        .ai { align-self: flex-end; background: #333; color: #00ff88; border: 1px solid #444; }
        .input-area { padding: 20px; background: #252525; display: flex; gap: 10px; }
        input { flex: 1; padding: 12px; border: none; border-radius: 5px; background: #333; color: white; outline: none; }
        button { background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">🤖 نظام أوليفير الذكي</div>
    <div id="chat-window"></div>
    <div class="input-area">
        <input type="text" id="msg-input" placeholder="اكتب شيئاً لنتذكره...">
        <button onclick="send()">إرسال</button>
    </div>

    <script>
        async function send() {
            const input = document.getElementById('msg-input');
            const window = document.getElementById('chat-window');
            if(!input.value) return;

            const text = input.value;
            window.innerHTML += `<div class="bubble user">${text}</div>`;
            input.value = '';

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await response = await res.json();
            window.innerHTML += `<div class="bubble ai">${data.reply}</div>`;
            window.scrollTop = window.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    try:
        conn = pymysql.connect(**DB_CONFIG, ssl={'ssl': True})
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS memory (content TEXT)")
            cursor.execute("INSERT INTO memory (content) VALUES (%s)", (user_msg,))
            conn.commit()
        conn.close()
        return jsonify({"reply": "تم الحفظ في ذاكرتك الرقمية بنجاح!"})
    except Exception as e:
        return jsonify({"reply": f"خطأ في الاتصال: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))