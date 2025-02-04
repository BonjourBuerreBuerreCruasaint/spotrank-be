from flask import Flask, jsonify, request, Blueprint
import mysql.connector
from flask_cors import CORS
from mysql.connector import pooling

# ✅ Flask 앱 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = 'welcome1!'
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# ✅ MySQL 연결 설정 (커넥션 풀 사용)
db_config = {
    'host': '15.164.175.70',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank'
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)

def get_db_connection():
    """MySQL 커넥션 풀에서 연결을 가져옴"""
    return connection_pool.get_connection()

# ✅ Blueprint 설정
sales_daily_blueprint = Blueprint('get_day_sales', __name__, url_prefix="/api")

# ✅ 요일별 매출 및 인기 메뉴 데이터 가져오기
@sales_daily_blueprint.route('/day-detail-sales', methods=['GET'])
def get_day_detail_sales():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 401

        print(f"📌 요청된 user_id: {user_id}")

        # ✅ 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ store_id 가져오기
        query_store = """
            SELECT stores.id AS store_id 
            FROM users 
            JOIN stores ON users.id = stores.id  
            WHERE users.id = %s
        """
        cursor.execute(query_store, (user_id,))
        user_store = cursor.fetchone()

        print(f"📌 사용자 매장 조회 결과: {user_store}")

        if not user_store:
            return jsonify({"error": "해당 사용자의 매장을 찾을 수 없습니다."}), 404

        store_id = user_store["store_id"]

        # ✅ 요일별 매출 데이터 조회 (LineChart)
        query_sales = """
            SELECT DAYNAME(hour_start) AS day, SUM(total_sales) AS sales
            FROM sales_daily
            WHERE store_id = %s
            GROUP BY day
            ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
        """
        cursor.execute(query_sales, (store_id,))
        sales_data = cursor.fetchall()

        print(f"📌 요일별 매출 데이터: {sales_data}")

        if not sales_data:
            return jsonify({"message": "해당 매장의 요일별 매출 데이터가 없습니다."}), 404

        # ✅ 요일별 인기 메뉴 데이터 조회 (BarChart)
        query_menu = """
            SELECT DAYNAME(hour_start) AS day, top_menu AS name, SUM(count) AS value
            FROM sales_daily
            WHERE store_id = %s
            GROUP BY day, name
            ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
        """
        cursor.execute(query_menu, (store_id,))
        menu_data = cursor.fetchall()

        print(f"📌 인기 메뉴 데이터: {menu_data}")

        return jsonify({
            "sales_chart": sales_data,  # ✅ 요일별 매출 데이터 (LineChart)
            "menu_chart": menu_data  # ✅ 요일별 인기 메뉴 데이터 (BarChart)
        }), 200

    except mysql.connector.Error as err:
        print(f"❌ 데이터베이스 오류: {err}")
        return jsonify({"error": "데이터베이스 오류가 발생했습니다."}), 500

    except Exception as e:
        print(f"❌ 알 수 없는 오류: {e}")
        return jsonify({"error": "알 수 없는 오류가 발생했습니다."}), 500

    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

# ✅ 블루프린트 등록
app.register_blueprint(sales_daily_blueprint)

# ✅ Flask 실행
if __name__ == '__main__':
    app.run(debug=True)