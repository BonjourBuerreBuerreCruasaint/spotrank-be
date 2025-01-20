from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import re
import pymysql
import bcrypt

# Flask App 초기화
app = Flask(__name__)
app.secret_key = 'welcome1!'
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

login_blueprint = Blueprint('login', __name__)  # API URL prefix


# MySQL Database Configuration
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='welcome1!',
        database='test_db',
        cursorclass=pymysql.cursors.DictCursor
    )


# Helper function to validate email
def validate_email(email):
    regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(regex, email) is not None


# 로그인 엔드포인트
@login_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "이메일 형식으로 입력해주세요"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = "SELECT id, password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                # stored_hashed_password = user['password'].encode('utf-8')
                # if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                if password == user['password']:
                    return jsonify({"message": "로그인 성공", "user_id": user['id']}), 200
                else:
                    return jsonify({"error": "비밀번호가 잘못되었습니다"}), 401
            else:
                return jsonify({"error": "등록되지 않은 이메일입니다"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "서버 오류"}), 500
    finally:
        conn.close()


# Flask 애플리케이션에 Blueprint 등록$
app.register_blueprint(login_blueprint, url_prefix='/api')  # URL Prefix 추가

if __name__ == '__main__':
    app.run(debug=True)