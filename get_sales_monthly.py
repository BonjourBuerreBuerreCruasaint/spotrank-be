from flask import Flask, jsonify, request, Blueprint
import mysql.connector
from flask_cors import CORS
from mysql.connector import pooling

# ✅ Flask 앱 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = 'welcome1!'  # Flask 시크릿 키 설정
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# ✅ MySQL 연결 설정 (커넥션 풀 사용)
db_config = {
    'host': '15.164.175.70',
    'port': 3306,
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
get_month_sales_blueprint = Blueprint('get_month_sales', __name__, url_prefix='/api')

# ✅ 월간 매출 및 인기 메뉴 데이터 가져오기
@get_month_sales_blueprint.route('/month-detail-sales', methods=['GET'])
def get_month_detail_sales():
    try:
        # 🔥 `user_id` 파라미터 확인
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 401

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

        if not user_store:
            return jsonify({"error": "해당 사용자의 매장을 찾을 수 없습니다."}), 404

        store_id = user_store["store_id"]

        # ✅ 월간 매출 데이터 조회
        query_sales = """
            SELECT year_month_ AS month, top_sales AS sales
            FROM monthly_sales
            WHERE store_id = %s
            ORDER BY month ASC;
        """
        cursor.execute(query_sales, (store_id,))
        sales_data = cursor.fetchall()

        if not sales_data:
            return jsonify({"message": "해당 매장의 월간 매출 데이터가 없습니다."}), 404

        # ✅ 월간 인기 메뉴 데이터 가져오기 (BarChart용)
        query_menu = """
            SELECT year_month_ AS month, top_menu AS name
            FROM monthly_sales
            WHERE store_id = %s
            ORDER BY month ASC;
        """
        cursor.execute(query_menu, (store_id,))
        menu_data_raw = cursor.fetchall()

        # ✅ 메뉴 데이터를 객체 형태로 변환
        menu_data = []
        for item in menu_data_raw:
            menu_list = item["name"].split(", ")
            for menu in menu_list:
                menu_name, count = menu.rsplit(" ", 1)  # 마지막 괄호 포함된 값 추출

                # ✅ 쉼표 제거 후 int 변환
                count = int(count.replace(",", "").replace("(", "").replace("개)", ""))

                menu_data.append({
                    "month": item["month"],
                    "name": menu_name,
                    "value": count
                })

        # ✅ JSON 응답 반환
        return jsonify({
            "sales_chart": sales_data,  # 월간 매출 데이터 (LineChart)
            "menu_chart": menu_data  # 월간 인기 메뉴 데이터 (BarChart)
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
app.register_blueprint(get_month_sales_blueprint)

# ✅ Flask 실행
if __name__ == '__main__':
    app.run(debug=True)