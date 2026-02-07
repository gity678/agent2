import os
from flask import Flask, render_template_string, request, jsonify
import pymysql

app = Flask(__name__)

# بيانات Aiven (تأكد من بقائها كما هي)
DB_CONFIG = {
    'host': 'mysql-colab-oliver59oliv-1ac2.f.aivencloud.com',
    'port': 23043,
    'user': 'avnadmin',
    'password': 'AVNS__uZT75lw-GrX9bxvmF1',
    'database': 'defaultdb',
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Oliver AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* إعدادات الخلفية وجعل المحتوى في المنتصف */
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #0d1117; 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
        }

        /* نافذة الدردشة الملمومة */
        .chat-container { 
            width: 90%; 
            max-width: 450px; /* العرض المحدد */
            height: 600px; /* الطول المحدد */
            background: #161b22; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
            display: flex; 
            flex-direction: column; 
            overflow: hidden;
            border: 1px solid #30363d;
        }

        .header { 
            background: #21262d; 
            padding: 15px; 
            text-align: center; 
            font-weight: bold; 
            color: #58a6ff;
            border-bottom: 1px solid #30363d;
        }

        #chat-window { 
            flex: 1; 
            overflow-y: auto; 
            padding: 15px; 
            display: flex; 
            flex-direction: column; 
            gap: 10px; 
            background-image: radial-gradient(#30363d 0.5px, transparent 0.5px);
            background-size: 20px 20px;
        }

        .bubble { 
            padding: 10px 15px; 
            border-radius: 15px; 
            max-width: 80%; 
            font-size: 14px; 
            line-height: 1.4;
        }

        .user { align-self: flex-start; background: #238636; color: white; border-bottom-right-radius: 2px; }
        .ai { align-self: flex-end; background: #30363d; color: #c9d1d9; border-bottom-left-radius: 2px; }

        .input-area { 
            padding: 15px; 
            background: #161b22; 
            display: flex; 
            gap: 8px; 
            border-top: 1px solid #30363d;
        }

        input { 
            flex: 1; 
            padding: 10px; 
            border-radius: 10px; 
            border: 1px solid #30363d; 
            background: #0d1117; 
            color: white; 
            outline: none; 
        }

        button { 
            background: #1f6feb; 
            color: white; 
            border: none; 
            padding: 0 15px; 
            border-radius: 10px; 
            cursor: pointer; 
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">🤖 مساعد أوليفير الذكي</div>
        <div id="chat-window"></div>
        <div class="input-area">
            <input type="text" id="msg-input" placeholder="اكتب هنا...">
            <button onclick="send()">إرسال</button>
        </div>
    </div>

    <script>
        async function send() {
            const input = document.getElementById('msg-input');
            const windowDiv = document.getElementById('chat-window');
            if(!input.value) return;

            const text = input.value;
            windowDiv.innerHTML += `<div class="bubble user">${text}</div>`;
            input.value = '';
            windowDiv.scrollTop = windowDiv.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                windowDiv.innerHTML += `<div class="bubble ai">${data.reply}</div>`;
                windowDiv.scrollTop = windowDiv.scrollHeight;
            } catch(e) {
                windowDiv.innerHTML += `<div class="bubble ai" style="color:red">خطأ في الاتصال!</div>`;
            }
        }
        document.getElementById('msg-input').addEventListener("keypress", (e) => { if(e.key === "Enter") send(); });
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

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
        return jsonify({"reply": "تم الحفظ في الذاكرة السحابية."})
    except Exception as e:
        return jsonify({"reply": f"خطأ: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))