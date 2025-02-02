from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import re
import pymysql
import bcrypt
import os  # 환경변수 가져오기

# Flask App 초기화
app = Flask(__name__)
app.secret_key = 'welcome1!'  # 세션 키 (필요시 사용)
CORS(app, resources={r"/api/*": {"origins": "http://spotrank.store"}}, supports_credentials=True)

login_blueprint = Blueprint('login', __name__)  # API URL prefix

# MySQL Database Configuration (환경변수로부터 DB 접속 정보 가져오기)
def get_db_connection():
    host = os.getenv('DATABASE_HOST')
    user = os.getenv('DATABASE_USER')
    password = os.getenv('DATABASE_PASSWORD')
    database = os.getenv('DATABASE_NAME')

    print(f"Connecting to DB at {host}...")  # DB 접속 확인
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )

# Helper function to validate email
def validate_email(email):
    regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(regex, email) is not None

# 로그인 엔드포인트
@login_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        print(f"Request data: {data}")  # 전달된 JSON 데이터 출력

        email = data.get('email')
        password = data.get('password')

        # 이메일 형식 검증
        if not validate_email(email):
            return jsonify({"error": "이메일 형식으로 입력해주세요"}), 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = "SELECT id, password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            print(f"User found: {user}")  # 찾은 사용자 출력

            if user:
                # bcrypt를 사용하여 해시된 비밀번호 확인
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    # 로그인 성공시 user_id 반환
                    return jsonify({"message": "로그인 성공", "user_id": user['id']}), 200
                else:
                    return jsonify({"error": "비밀번호가 잘못되었습니다"}), 401
            else:
                return jsonify({"error": "등록되지 않은 이메일입니다"}), 404

    except Exception as e:
        print(f"Error occurred: {e}")  # 발생한 오류 출력
        return jsonify({"error": "서버 오류"}), 500
    finally:
        conn.close()

# Flask 애플리케이션에 Blueprint 등록
app.register_blueprint(login_blueprint, url_prefix='/api')  # URL Prefix 추가

if __name__ == '__main__':
    app.run(debug=True)
