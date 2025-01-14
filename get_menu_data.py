from flask import Flask, jsonify, request, session, Blueprint
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Welcome1!'  # Flask 시크릿 키 설정
get_menu_data_blueprint = Blueprint('get_menu_data', __name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# MySQL 연결 설정
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

# API 엔드포인트: 메뉴 데이터 가져오기
@get_menu_data_blueprint.route('/get-menu-data', methods=['GET'])
def get_menu_data():
    if 'id' not in session:
        return jsonify({"error": "세션에 로그인 ID가 없습니다."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu WHERE ceo_id = %s", (session['id'],))
        menus = cursor.fetchall()
        conn.close()
        if not menus:
            return jsonify({"message": "데이터가 없습니다."}), 404  # 빈 데이터 처리

        menu_data = [
            {
                "ceo_id": menu['ceo_id'],
                "name": menu['name'],
                "price": menu['price'],
                "total_count": menu['total_count'],
                "total_sales": menu['total_sales']
            }
            for menu in menus
        ]
        return jsonify(menu_data), 200

    except mysql.connector.Error as err:
        print(f"데이터베이스 오류: {err}")
        return jsonify({"error": "데이터베이스 오류가 발생했습니다."}), 500

    except Exception as e:
        print(f"알 수 없는 오류: {e}")
        return jsonify({"error": "알 수 없는 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    app.run(debug=True)