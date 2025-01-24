from flask import Blueprint, jsonify,Flask
import mysql.connector
from flask_cors import CORS
# Blueprint 설정
api_blueprint = Blueprint('api', __name__)

CORS(api_blueprint, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# MySQL 데이터베이스 연결 설정
db_config = {
    'host': '13.209.87.204',
    'user': 'root',  # MySQL 사용자 이름
    'password': 'Welcome1!',  # MySQL 비밀번호
    'database': 'spotrank'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@api_blueprint.route('/api/ranking', methods=['GET'])
def get_ranking():
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ranking")
        data = cursor.fetchall()

        # 카테고리별 랭킹 계산
        cafe_ranking = [
            {
                "shop_name": row["shop_name"],
                "total": row["quantity"],
                "category": row["category"]
            }
            for row in data if row["category"] == "cafe"
        ]
        restaurant_ranking = [
            {
                "shop_name": row["shop_name"],
                "total": row["quantity"],
                "category": row["category"]
            }
            for row in data if row["category"] == "restaurant"
        ]

        # 카페와 레스토랑 랭킹을 각각 판매량 기준으로 내림차순 정렬하고, 상위 10개만 가져옴
        sorted_cafe_ranking = sorted(cafe_ranking, key=lambda x: x["total"], reverse=True)[:10]
        sorted_restaurant_ranking = sorted(restaurant_ranking, key=lambda x: x["total"], reverse=True)[:10]

        # 하위 5개 판매량
        bottom_ranking = sorted(data, key=lambda x: x["quantity"])[:5]

        return jsonify({
            "cafe_ranking": sorted_cafe_ranking,
            "restaurant_ranking": sorted_restaurant_ranking,
            "bottom_ranking": bottom_ranking
        })

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

app = Flask(__name__)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)