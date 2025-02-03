from flask import Flask, jsonify, request, Blueprint
import mysql.connector
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'welcome1!'  # Flask 시크릿 키 설정
get_menu_data_blueprint = Blueprint('get_menu_data', __name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://spotrank.store"}})

# MySQL 연결 설정
db_config = {
    'host': '13.209.87.204',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank.store'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"MySQL 연결 실패: {err}")
        raise

# API 엔드포인트: 하루 동안의 누적 판매 데이터 반환
@get_menu_data_blueprint.route('/get-menu-data', methods=['GET'])
def get_daily_sales_data():
    try:
        # Authorization 헤더에서 user_id 가져오기
        user_id = request.headers.get('Authorization')
        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 401

        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 하루 누적 데이터를 가져오는 쿼리
        query = """
        SELECT 
            menu_name AS name,
            price,
            COUNT(*) AS total_count,
            SUM(price) AS total_sales
        FROM 
            sales_data
        WHERE 
            user_id = %s
            AND DATE(order_time) = CURDATE()
        GROUP BY 
            menu_name, price
        ORDER BY 
            total_sales DESC;
        """
        print(f"Executing query with user_id: {user_id}")
        cursor.execute(query, (user_id,))
        daily_sales = cursor.fetchall()
        print(f"Query result: {daily_sales}")

        if not daily_sales:
            return jsonify({"message": "오늘의 판매 데이터가 없습니다."}), 404

        # 결과 데이터 반환
        return jsonify(daily_sales), 200

    except mysql.connector.Error as err:
        print(f"데이터베이스 오류: {err}")
        return jsonify({"error": "데이터베이스 오류가 발생했습니다."}), 500

    except Exception as e:
        print(f"알 수 없는 오류: {e}")
        return jsonify({"error": "알 수 없는 오류가 발생했습니다."}), 500

    finally:
        if 'conn' in locals():
            conn.close()

# 블루프린트 등록
app.register_blueprint(get_menu_data_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)