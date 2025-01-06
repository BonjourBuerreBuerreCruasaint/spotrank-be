from flask import Flask, request, jsonify, session, Blueprint
from flask_cors import CORS
import re
import pymysql
import bcrypt

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

login_blueprint = Blueprint('login', __name__)  # API URL prefix

# MySQL Database Configuration
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='y2kxtom16spu!',
        database='info',
        cursorclass=pymysql.cursors.DictCursor
    )

# Helper function to validate email
def validate_email(email):
    regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(regex, email) is not None

@login_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    session['email'] = email
    session['isLoggedIn'] = True

    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "이메일 형식으로 입력해주세요"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                stored_hashed_password = user['password'].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    session['isLoggedIn'] = True
                    session['email'] = email
                    return jsonify({"message": "로그인 성공", "email": email}), 200
                else:
                    return jsonify({"error": "비밀번호가 잘못되었습니다"}), 401
            else:
                return jsonify({"error": "등록되지 않은 이메일입니다"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "서버 오류"}), 500
    finally:
        conn.close()

@login_blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop('isLoggedIn', None)
    session.pop('email', None)
    return jsonify({"message": "로그아웃 성공"}), 200

@login_blueprint.route('/status', methods=['GET'])
def status():
    if session.get('isLoggedIn'):
        return jsonify({"loggedIn": True, "email": session.get('email')}), 200
    else:
        return jsonify({"loggedIn": False}), 200

app.register_blueprint(login_blueprint)

if __name__ == '__main__':
    app.run(debug=True)