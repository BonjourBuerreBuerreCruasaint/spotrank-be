import random
import pandas as pd
import os
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

# 데이터 저장소
data_storage = []

# 데이터 샘플 리스트
PREDEFINED_DATA = [
    {"owner_id": "owner001", "category_id": 1, "data": {"menu": "Pizza", "quantity": 2, "price": 15.5, "timestamp": "2024-12-27 14:00:00"}},
    {"owner_id": "owner002", "category_id": 2, "data": {"상품명": "Latte", "개수": 1, "판매가격": 4.5, "판매시간": "2024-12-27 14:05:00"}},
    {"owner_id": "owner003", "category_id": 1, "data": {"menu_name": "Burger", "quantity_sold": 3, "price_per_item": 10.0, "time": "2024-12-27 14:10:00"}},
    {"owner_id": "owner001", "category_id": 1, "data": {"menu": "Salad", "quantity": 1, "price": 12.0, "timestamp": "2024-12-27 14:15:00"}},
    {"owner_id": "owner002", "category_id": 2, "data": {"상품명": "Espresso", "개수": 2, "판매가격": 3.0, "판매시간": "2024-12-27 14:20:00"}}
]

# 데이터 저장 경로
OUTPUT_DIR = "output_data"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 매출 데이터 랜덤 생성 및 전송 스레드
def simulate_sales():
    while True:
        try:
            # PREDEFINED_DATA에서 랜덤으로 하나 선택
            selected_data = random.choice(PREDEFINED_DATA)
            print(f"Selected data: {selected_data}")
            data_storage.append(selected_data)  # 선택된 데이터를 data_storage에 추가
        except Exception as e:
            print(f"Error in simulate_sales: {e}")
        threading.Event().wait(6)  # 6초 대기

# 데이터 저장 함수
def save_data_periodically():
    while True:
        threading.Event().wait(3600)  # 1시간 대기
        if data_storage:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_file = os.path.join(OUTPUT_DIR, f"sales_data_{timestamp}.csv")
            json_file = os.path.join(OUTPUT_DIR, f"sales_data_{timestamp}.json")

            # 데이터를 원본 컬럼 구조로 저장
            raw_data = [{"owner_id": record["owner_id"], "category_id": record["category_id"], **record["data"]} for
                        record in data_storage]

            # DataFrame 생성
            df = pd.DataFrame(raw_data)

            # CSV 및 JSON으로 저장
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            df.to_json(json_file, orient='records', force_ascii=False)

            print(f"Data saved to {csv_file} and {json_file}")
            data_storage.clear()  # 저장 후 데이터 초기화

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
    # 스레드 실행
    threading.Thread(target=simulate_sales, daemon=True).start()
    threading.Thread(target=save_data_periodically, daemon=True).start()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)