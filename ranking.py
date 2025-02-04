from flask import Blueprint, jsonify, Flask
import mysql.connector
import random
from flask_cors import CORS

# ✅ Blueprint 설정
api_blueprint = Blueprint('api', __name__)
CORS(api_blueprint, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# ✅ MySQL 데이터베이스 연결 설정
db_config = {
    'host': '15.164.175.70',
    'user': 'root',  # MySQL 사용자 이름
    'password': 'Welcome1!',  # MySQL 비밀번호
    'database': 'spotrank'
}

def get_db_connection():
    """ MySQL 데이터베이스 연결 """
    return mysql.connector.connect(**db_config)

@api_blueprint.route('/api/ranking', methods=['GET'])
def get_ranking():
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor(dictionary=True)

        # ✅ 오늘 날짜의 전체 매출 데이터 가져오기
        # ✅ 데이터 정렬을 확실히 유지하도록 ORDER BY 적용
        query = """
            SELECT store_id, store_name, total_sales, top_menu, hour_start, latitude, longitude, category
            FROM sales_hourly
            WHERE DATE(hour_start) = CURDATE()
            ORDER BY total_sales DESC, store_name ASC;  # ✅ 항상 같은 순서 유지
        """
        cursor.execute(query)
        all_shops = cursor.fetchall()

        if not all_shops:
            return jsonify({"message": "오늘의 데이터가 없습니다. sales_hourly 테이블을 업데이트하세요."}), 404

        # ✅ 카테고리별 정렬된 랭킹 저장 (대소문자 및 공백 정리)
        category_rankings = {
            "restaurants": [],
            "cafes": []
        }

        for shop in all_shops:
            category = shop["category"].strip().lower()  # ✅ 공백 제거 & 소문자로 변환
            if "음식점" in category or "restaurant" in category:
                category_rankings["restaurants"].append(shop)
            elif "카페" in category or "cafe" in category:
                category_rankings["cafes"].append(shop)

        # ✅ 각 카테고리별 상위 10개 매장 정렬
        category_rankings["restaurants"] = sorted(category_rankings["restaurants"], key=lambda x: x["total_sales"], reverse=True)[:10]
        category_rankings["cafes"] = sorted(category_rankings["cafes"], key=lambda x: x["total_sales"], reverse=True)[:10]

        # ✅ 핫플레이스 10개 랜덤 선택 (데이터 부족 시 모든 값 사용)
        hot_places = random.sample(all_shops, min(10, len(all_shops)))

        # ✅ 오늘 날짜의 하위 20개 매출 데이터 가져오기
        bottom_20_shops = sorted(all_shops, key=lambda x: x["total_sales"])[:20]

        return jsonify({
            "restaurant_ranking": category_rankings["restaurants"],  # 🍽️ 레스토랑 10개
            "cafe_ranking": category_rankings["cafes"],  # ☕ 카페 10개
            "hot_places": hot_places,  # 🔥 핫플레이스 10개
            "bottom_ranking": bottom_20_shops  # 🥶 하위 20개 매장 추가
        })

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# ✅ Flask 앱 실행
app = Flask(__name__)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)