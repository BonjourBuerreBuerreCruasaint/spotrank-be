from flask import Flask, request, jsonify, Blueprint
import mysql.connector
import bcrypt
from flask_cors import CORS  # flask_cors에서 CORS 가져오기

app = Flask(__name__)
# bcrypt = Bcrypt(app)

# CORS 설정 (모든 /api/* 경로에 대해 localhost:3000에서 오는 요청을 허용)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
signup_blueprint = Blueprint('signup', __name__)

db_config = {
    'host': "13.209.87.204",
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank'

}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"MySQL 연결 실패: {err}")
        raise

@signup_blueprint.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json  # JSON 데이터 받기
        print(f"📌 요청된 데이터: {data}")  # 🔥 받은 데이터 로그 출력

        if not data:
            return jsonify({'message': '잘못된 요청: JSON 데이터가 없습니다.'}), 400

        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')
        username = data.get('username')
        birthdate = data.get('birthdate')
        phone = data.get('phone')

        print(f"📌 필드 값: email={email}, password={password}, confirm_password={confirm_password}, username={username}, birthdate={birthdate}, phone={phone}")  # 🔥 필드 값 출력

        # 필수 필드 확인
        if not all([email, password, confirm_password, username, birthdate, phone]):
            return jsonify({'message': '모든 필드를 입력해야 합니다.'}), 400

        if password != confirm_password:
            return jsonify({'message': '비밀번호가 일치하지 않습니다.'}), 400

        # 비밀번호 해시화
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # 데이터베이스 연결
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

        cursor.close()
        connection.close()

        return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.'}), 201

    except mysql.connector.Error as err:
        print(f"❌ 데이터베이스 오류: {err}")
        return jsonify({'message': f'회원가입 중 오류 발생: {err}'}), 500

    except Exception as e:
        print(f"❌ 예기치 않은 오류 발생: {e}")
        return jsonify({'message': '회원가입 중 예기치 않은 오류가 발생했습니다.'}), 500
app.register_blueprint(signup_blueprint)

if __name__ == '__main__':
    app.run(debug=True)