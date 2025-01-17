from flask import Flask, jsonify, request, Blueprint
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'welcome1!'  # Flask 시크릿 키 설정
get_menu_data_blueprint = Blueprint('get_menu_data', __name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# MySQL 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'welcome1!',
    'database': 'test_db'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"MySQL 연결 실패: {err}")
        raise

# API 엔드포인트: 메뉴 데이터 가져오기
@get_menu_data_blueprint.route('/get-menu-data', methods=['GET'])
def get_menu_data():
    try:
        # Authorization 헤더에서 user_id 가져오기
        user_id = request.headers.get('Authorization')
        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 401

        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 메뉴 데이터 쿼리
        cursor.execute("SELECT * FROM menu WHERE ceo_id = %s", (user_id,))
        menus = cursor.fetchall()

        if not menus:
            return jsonify({"message": "데이터가 없습니다."}), 404

        # 결과 데이터 반환
        return jsonify(menus), 200

    except mysql.connector.Error as err:
        print(f"데이터베이스 오류: {err}")
        return jsonify({"error": "데이터베이스 오류가 발생했습니다."}), 500

    except Exception as e:
        print(f"알 수 없는 오류: {e}")
        return jsonify({"error": "알 수 없는 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    app.run(debug=True)