from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_bcrypt import Bcrypt
from flask_cors import cross_origin

app = Flask(__name__)
bcrypt = Bcrypt(app)

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
@cross_origin(origin='http://localhost:3000')
def signup():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    email = data.get('id')
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
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_db_connection()
        cursor = connection.cursor()

        # 중복된 이메일 확인
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'message': '이미 등록된 이메일입니다.'}), 400

        cursor.execute("""
            INSERT INTO users (email, password, phone, birthdate, username)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, hashed_password, phone, birthdate, username))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.'}), 201
    except mysql.connector.Error as err:
        return jsonify({'message': f'회원가입 중 오류 발생: {err}'}), 500

app.register_blueprint(join_blueprint)

if __name__ == '__main__':
    app.run(debug=True)