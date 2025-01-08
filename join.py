from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_bcrypt import Bcrypt
import bcrypt
from flask_cors import CORS  # flask_cors에서 CORS 가져오기

app = Flask(__name__)
# bcrypt = Bcrypt(app)

# CORS 설정 (모든 /api/* 경로에 대해 localhost:3000에서 오는 요청을 허용)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

join_blueprint = Blueprint('join', __name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'y2kxtom16spu!',
    'database': 'info'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"MySQL 연결 실패: {err}")
        raise

@join_blueprint.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        # CORS pre-flight 요청을 처리
        return '', 200

    data = request.json
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')
    username = data.get('username')
    birthdate = data.get('birthdate')
    phone = data.get('phone')

    if not all([email, password, confirm_password, username, birthdate, phone]):
        return jsonify({'message': '모든 필드를 입력해야 합니다.'}), 400

    if password != confirm_password:
        return jsonify({'message': '비밀번호가 일치하지 않습니다.'}), 400

    try:
        # 비밀번호 해시화
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        connection = get_db_connection()
        cursor = connection.cursor()

        # 중복된 이메일 확인
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'message': '이미 등록된 이메일입니다.'}), 400

        # 사용자 데이터 삽입
        cursor.execute("""
            INSERT INTO users (email, password, phone, birthdate, username)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, hashed_password, phone, birthdate, username))
        connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.',
                        'id': user_id}), 201
    except mysql.connector.Error as err:
        print(f"Database error: {err}")  # 추가된 로그
        return jsonify({'message': f'회원가입 중 오류 발생: {err}'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")  # 예기치 않은 오류 출력
        return jsonify({'message': '회원가입 중 예기치 않은 오류가 발생했습니다.'}), 500
app.register_blueprint(join_blueprint)

if __name__ == '__main__':
    app.run(debug=True)