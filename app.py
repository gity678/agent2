import os
from flask import Flask, render_template_string, request, jsonify
import pymysql

app = Flask(__name__)

# بيانات Aiven (يفضل وضعها في Environment Variables في Railway لاحقاً)
DB_CONFIG = {
    'host': 'mysql-colab-oliver59oliv-1ac2.f.aivencloud.com',
    'port': 23043,
    'user': 'avnadmin',
    'password': 'AVNS__uZT75lw-GrX9bxvmF1',
    'database': 'defaultdb',
}

@app.route('/')
def home():
    return "<h1>AI Oliver is Running!</h1>" # أو كود HTML الواجهة الذي صممناه

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    conn = pymysql.connect(**DB_CONFIG, ssl={'ssl': True})
    with conn.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS chat_log (msg TEXT)")
        cursor.execute("INSERT INTO chat_log (msg) VALUES (%s)", (user_msg,))
        conn.commit()
    conn.close()
    return jsonify({"reply": f"Saved to Aiven: {user_msg}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
