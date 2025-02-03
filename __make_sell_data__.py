import random
import threading
from flask import Flask, jsonify, Blueprint
from datetime import datetime
import mysql.connector


# 데이터베이스 연결 설정
db_config = {
    'host': '15.164.175.70',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank',
    'auth_plugin': 'mysql_native_password'

}

# MySQL 테이블 생성 함수
def create_sales_table():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # sales_data 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sales_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            menu_name VARCHAR(255),
            price DECIMAL(10, 2),
            order_time DATETIME,
            quantity INT
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table `sales_data` is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# 모든 order_* 테이블을 sales_data 테이블로 합치는 함수
def merge_order_tables():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # order_* 테이블 이름 가져오기
        cursor.execute("SHOW TABLES WHERE Tables_in_spotrank LIKE 'order_%'")
        order_tables = [row[0] for row in cursor.fetchall()]

        if not order_tables:
            print("No order tables found.")
            return

        # 각 order 테이블 데이터를 sales_data에 삽입
        for table_name in order_tables:
            # user_id는 테이블 이름에서 추출
            user_id = int(table_name.split('_')[1])

            # order_* 테이블의 데이터 가져오기
            select_query = f"SELECT menu, price, order_time, count FROM {table_name}"
            cursor.execute(select_query)
            orders = cursor.fetchall()

            # sales_data 테이블에 삽입
            insert_query = """
                INSERT INTO sales_data (user_id, menu_name, price, order_time, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """
            sales_data = [
                (user_id, row[0], row[1], row[2], row[3]) for row in orders
            ]
            cursor.executemany(insert_query, sales_data)
            conn.commit()
            print(f"Data from {table_name} merged into sales_data.")
    except Exception as e:
        print(f"Error merging order tables: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask 애플리케이션 설정
app = Flask(__name__)

@app.route('/merge', methods=['GET'])
def merge_tables_endpoint():
    merge_order_tables()
    return jsonify({"message": "All order_* tables merged into sales_data."})

if __name__ == "__main__":

    # sales_data 테이블 생성
    create_sales_table()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)

# import random
# import mysql.connector
# from datetime import datetime, timedelta
#
# # ✅ MySQL 데이터베이스 연결 설정
# db_config = {
#     'host': '15.164.175.70',
#     'user': 'root',
#     'password': 'Welcome1!',
#     'database': 'spotrank',
#     'auth_plugin': 'mysql_native_password'
# }
#
# # ✅ 메뉴 및 랜덤 가격 설정
# MENU_ITEMS = [
#     {"menu_name": "크루아상", "price": random.randint(3000, 8000)},
#     {"menu_name": "도넛", "price": random.randint(3000, 8000)},
#     {"menu_name": "머핀", "price": random.randint(3000, 8000)},
#     {"menu_name": "치즈케이크", "price": random.randint(3000, 8000)},
#     {"menu_name": "타르트", "price": random.randint(3000, 8000)},
# ]
#
# # ✅ 랜덤 주문 시간 생성 함수 (2024년 ~ 2025년 날짜)
# def random_order_time():
#     start_date = datetime(2024, 1, 1)  # 시작 날짜: 2024년 1월 1일
#     end_date = datetime(2025, 12, 31, 23, 59, 59)  # 종료 날짜: 2025년 12월 31일 23:59:59
#     random_days = random.randint(0, (end_date - start_date).days)  # 2024~2025년 내에서 랜덤한 날짜 선택
#     random_hour = random.randint(6, 23)  # 06시 ~ 23시 사이
#     random_minute = random.randint(0, 59)
#     random_second = random.randint(0, 59)
#     return start_date + timedelta(days=random_days, hours=random_hour, minutes=random_minute, seconds=random_second)
#
# # ✅ 100만 건의 데이터 생성 및 삽입
# def insert_dummy_sales_data(num_entries=100000):
#     conn = None
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
#
#         insert_query = """
#             INSERT INTO sales_data (user_id, menu_name, price, order_time, quantity)
#             VALUES (%s, %s, %s, %s, %s)
#         """
#
#         sales_data = []
#         for _ in range(num_entries):
#             menu_item = random.choice(MENU_ITEMS)
#             menu_name = menu_item["menu_name"]
#             price = menu_item["price"]
#             order_time = random_order_time()  # ✅ 2024~2025년 날짜에서 랜덤 선택
#             quantity = random.randint(1, 10)  # 1~10개 랜덤 수량
#
#             sales_data.append((1, menu_name, price, order_time, quantity))
#
#             # ✅ 5000개씩 배치 삽입 (성능 최적화)
#             if len(sales_data) >= 5000:
#                 cursor.executemany(insert_query, sales_data)
#                 conn.commit()
#                 print(f"✅ {len(sales_data)}개 데이터 삽입 완료...")
#                 sales_data = []  # 리스트 초기화
#
#         # 남은 데이터 삽입
#         if sales_data:
#             cursor.executemany(insert_query, sales_data)
#             conn.commit()
#             print(f"✅ 최종 {len(sales_data)}개 데이터 삽입 완료...")
#
#     except Exception as e:
#         print(f"❌ 데이터 삽입 오류: {e}")
#
#     finally:
#         if conn and conn.is_connected():
#             cursor.close()
#             conn.close()
#             print("✅ 데이터베이스 연결 종료.")
#
# # 🚀 실행
# if __name__ == "__main__":
#     insert_dummy_sales_data(100000)  # 100만 건 삽입