import mysql.connector
from flask import Flask, request, jsonify, Blueprint, session
import bcrypt
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://spotrank.store"}})

reset_password_blueprint = Blueprint('reset_password', __name__)

# MySQL 데이터베이스 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host='13.209.87.204',  # MySQL 호스트 (로컬 서버일 경우 'localhost' 사용)
        user='root',       # MySQL 사용자
        password='Welcome1!',  # MySQL 비밀번호
        database='spotrank'   # 사용할 데이터베이스
    )

# 새 비밀번호 설정
@reset_password_blueprint.route('/reset-password', methods=['POST'])
def reset_password():
    email = session['email']
    new_password = request.json.get('newPassword')
    print("email",email)

    if not email or not new_password:
        return jsonify({'message': '이메일과 새 비밀번호를 모두 제공해야 합니다.'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # 이메일로 사용자 확인
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': '사용자를 찾을 수 없습니다.'}), 404

        # 새 비밀번호를 해시하고 업데이트
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        print(hashed_password)
        print(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        connection.commit()

        return jsonify({'message': '비밀번호가 성공적으로 변경되었습니다.'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': '서버에서 오류가 발생했습니다.'}), 500

    finally:
        cursor.close()
        connection.close()

# 블루프린트 등록
app.register_blueprint(reset_password_blueprint)

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True)