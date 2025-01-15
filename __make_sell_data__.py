import random
import threading
from flask import Flask, jsonify, Blueprint
from datetime import datetime
import mysql.connector

make_sell_data_blueprint = Blueprint('make_sell_data', __name__)

# 데이터베이스 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'test_db'
}

# 데이터 샘플 리스트
PREDEFINED_DATA = [
    {"owner_id": "owner001", "category_id": 1, "data": {"menu": "Pizza", "quantity": 2, "price": 15.5, "timestamp": "2024-12-27 14:00:00"}},
    {"owner_id": "owner002", "category_id": 2, "data": {"상품명": "Latte", "개수": 1, "판매가격": 4.5, "판매시간": "2024-12-27 14:05:00"}},
    {"owner_id": "owner003", "category_id": 1, "data": {"menu_name": "Burger", "quantity_sold": 3, "price_per_item": 10.0, "time": "2024-12-27 14:10:00"}},
    {"owner_id": "owner001", "category_id": 1, "data": {"menu": "Salad", "quantity": 1, "price": 12.0, "timestamp": "2024-12-27 14:15:00"}},
    {"owner_id": "owner002", "category_id": 2, "data": {"상품명": "Espresso", "개수": 2, "판매가격": 3.0, "판매시간": "2024-12-27 14:20:00"}}
]

# MySQL 테이블 생성 함수
def create_table():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sales_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            owner_id VARCHAR(50) NOT NULL,
            category_id INT NOT NULL,
            menu_name VARCHAR(255),
            quantity INT,
            price DECIMAL(10, 2),
            timestamp DATETIME
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table `sales_data` is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 매출 데이터 랜덤 생성 및 전송 스레드
def simulate_sales():
    while True:
        try:
            # PREDEFINED_DATA에서 랜덤으로 하나 선택
            selected_data = random.choice(PREDEFINED_DATA)
            print(f"Selected data: {selected_data}")
            save_to_database(selected_data)  # 선택된 데이터를 MySQL에 저장
        except Exception as e:
            print(f"Error in simulate_sales: {e}")
        threading.Event().wait(6)  # 6초 대기

# MySQL에 데이터 저장 함수
def save_to_database(data):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 데이터 삽입 쿼리 작성
        query = """
            INSERT INTO sales_data (owner_id, category_id, menu_name, quantity, price, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        # 데이터 매핑 (다양한 키를 처리하기 위해 조건부로 매핑)
        owner_id = data["owner_id"]
        category_id = data["category_id"]
        menu_name = data["data"].get("menu") or data["data"].get("menu_name") or data["data"].get("상품명")
        quantity = data["data"].get("quantity") or data["data"].get("quantity_sold") or data["data"].get("개수")
        price = data["data"].get("price") or data["data"].get("price_per_item") or data["data"].get("판매가격")
        timestamp = data["data"].get("timestamp") or data["data"].get("time") or data["data"].get("판매시간")

        # 쿼리 실행
        cursor.execute(query, (owner_id, category_id, menu_name, quantity, price, timestamp))
        conn.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 카테고리 이름 조회 함수
def get_category_name(category_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT category_name FROM categories WHERE category_id = %s", (category_id,))
        result = cursor.fetchone()
        return result['category_name'] if result else None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Flask 애플리케이션 설정
app = Flask(__name__)
app.register_blueprint(make_sell_data_blueprint)

if __name__ == "__main__":
    # 테이블 생성
    create_table()

    # 스레드 실행
    threading.Thread(target=simulate_sales, daemon=True).start()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)
