from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import re
import pymysql
import bcrypt
import os
from dotenv import load_dotenv

# .env 파일 로드 (필요한 경우)
load_dotenv()

# Flask App 초기화
app = Flask(__name__)
app.secret_key = 'welcome1!'
CORS(app, resources={r"/api/*": {"origins": "http://spotrank.store"}}, supports_credentials=True)

login_blueprint = Blueprint('login', __name__)

# MySQL Database Configuration (환경변수로부터 DB 접속 정보 가져오기)
def get_db_connection():
    host = os.getenv('DATABASE_HOST')
    user = os.getenv('DATABASE_USER')
    password = os.getenv('DATABASE_PASSWORD')
    database = os.getenv('DATABASE_NAME')

    print(f"Connecting to DB at {host}...")
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
    conn = None  # conn 초기화
    try:
        data = request.json
        print(f"Request data: {data}")

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "이메일과 비밀번호를 모두 입력해주세요"}), 400

        if not validate_email(email):
            return jsonify({"error": "이메일 형식으로 입력해주세요"}), 400

        # 데이터베이스 연결 시도
        try:
            conn = get_db_connection()
        except Exception as db_connect_error:
            print(f"Failed to connect to the database: {db_connect_error}")
            return jsonify({"error": "데이터베이스 연결에 실패했습니다"}), 500

        # 사용자 조회 및 비밀번호 검증
        with conn.cursor() as cursor:
            query = "SELECT id, password FROM users WHERE email = %s"
            print(f"Executing query: {query} with email: {email}")
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    return jsonify({"message": "로그인 성공", "user_id": user['id']}), 200
                else:
                    return jsonify({"error": "비밀번호가 잘못되었습니다"}), 401
            else:
                return jsonify({"error": "등록되지 않은 이메일입니다"}), 404

    except pymysql.MySQLError as db_error:
        print(f"Database error occurred: {db_error}")
        return jsonify({"error": "데이터베이스 오류"}), 500
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "서버 오류"}), 500
    finally:
        # conn이 초기화된 경우에만 닫기
        if conn is not None:
            try:
                conn.close()
                print("Database connection closed.")
            except Exception as close_error:
                print(f"Error closing connection: {close_error}")

# Flask 애플리케이션에 Blueprint 등록
app.register_blueprint(login_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
