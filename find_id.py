from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

find_id_blueprint = Blueprint('find_id', __name__)

# MySQL 데이터베이스 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  # MySQL 호스트 (로컬 서버일 경우 'localhost' 사용)
        user='root',       # MySQL 사용자
        password='y2kxtom16spu!',  # MySQL 비밀번호
        database='info'   # 사용할 데이터베이스
    )

@find_id_blueprint.route('/find-id', methods=['POST'])
def find_id():
    # 클라이언트로부터 전달받은 데이터
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')

    if not name or not phone:
        return jsonify({'error': '이름과 전화번호는 필수 입력 사항입니다.'}), 400

    # 데이터베이스에서 사용자 조회
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT email FROM users 
        WHERE username = %s AND phone = %s
    ''', (name, phone))

    user = cursor.fetchone()
    conn.close()

    if user:
        # 사용자가 존재하면 이메일 반환
        return jsonify({'email': user['email']}), 200
    else:
        # 사용자 정보가 일치하지 않으면 에러 메시지 반환
        return jsonify({'error': '일치하는 사용자 정보가 없습니다.'}), 404


app.register_blueprint(find_id_blueprint)

if __name__ == '__main__':
    app.run(debug=True)