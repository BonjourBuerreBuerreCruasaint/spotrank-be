import pandas as pd
import random
from datetime import datetime, timedelta
import mysql.connector
import re

# MySQL 데이터베이스 연결
connection = mysql.connector.connect(
    host='localhost',  # MySQL 호스트
    user='root',  # MySQL 사용자 이름
    password='Welcome1!',  # MySQL 비밀번호
    database='test_db'  # 사용할 데이터베이스 이름
)

# SQL 쿼리를 사용하여 'filtered_store_info' 테이블 읽기
query = "SELECT * FROM filtered_store_info"
data = pd.read_sql(query, connection)

# 업종 소분류별 메뉴 목록 정의
menu_dict = {
    "일식 면 요리": ["라멘", "우동", "소바", "탄탄멘"],
    "카페": ["아메리카노", "카푸치노", "케이크", "라떼", "핫초코"],
    # ... (기타 업종 소분류는 생략)
}

# 랜덤 가격 생성 함수
def random_price():
    return int(random.randint(10, 500) * 100)  # 1,000원 ~ 50,000원

# 랜덤 수량 생성 함수
def random_count():
    return random.randint(1, 30)  # 1부터 30까지의 랜덤 수량

# 랜덤 주문 시간 생성 함수
def random_order_time():
    now = datetime.now()
    random_minutes = random.randint(0, 1440)  # 하루(24시간) 내에서 랜덤 분
    return now - timedelta(minutes=random_minutes)

# 테이블 생성 함수
def create_table(cursor, table_name, schema):
    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
    cursor.execute(create_query)

# 메뉴 및 주문 데이터를 MySQL에 저장
cursor = connection.cursor()

# 메뉴 테이블 스키마 정의 및 생성
menu_table_name = "menu_data"
menu_schema = """
    store_name VARCHAR(255),
    menu VARCHAR(255),
    price INT
"""
create_table(cursor, menu_table_name, menu_schema)

# 주문 테이블 스키마 정의 및 생성
order_table_name = "order_data"
order_schema = """
    store_name VARCHAR(255),
    menu VARCHAR(255),
    price INT,
    order_time DATETIME,
    count INT
"""
create_table(cursor, order_table_name, order_schema)

# 기타 메뉴 제외하고 저장
for _, row in data.iterrows():
    try:
        # 상호명과 업종 소분류 추출
        store_name = row["상호명"]
        sub_category = row["상권업종소분류명"]

        # 메뉴와 가격 데이터 생성
        menus = menu_dict.get(sub_category, ["기타 메뉴"])
        if "기타 메뉴" in menus:
            continue  # 기타 메뉴만 있는 업종은 건너뜀

        menu_data = [{"store_name": store_name, "menu": menu, "price": random_price()} for menu in menus]

        # 주문 데이터 생성 (100개)
        order_data = []
        for _ in range(100):
            selected_menu = random.choice(menu_data)
            order_data.append({
                "store_name": store_name,
                "menu": selected_menu["menu"],
                "price": selected_menu["price"],
                "order_time": random_order_time(),
                "count": random_count(),
            })

        # 메뉴 데이터 삽입
        for menu in menu_data:
            cursor.execute(
                f"INSERT INTO {menu_table_name} (store_name, menu, price) VALUES (%s, %s, %s)",
                (menu["store_name"], menu["menu"], menu["price"])
            )

        # 주문 데이터 삽입
        for order in order_data:
            cursor.execute(
                f"INSERT INTO {order_table_name} (store_name, menu, price, order_time, count) VALUES (%s, %s, %s, %s, %s)",
                (order["store_name"], order["menu"], order["price"], order["order_time"], order["count"])
            )

    except KeyError as e:
        print(f"누락된 키 오류 발생: {e}")
    except Exception as e:
        print(f"오류 발생: {e}")

# 변경 사항 커밋 및 연결 종료
connection.commit()
cursor.close()
connection.close()

print(f"메뉴 및 주문 데이터가 '{menu_table_name}'와 '{order_table_name}' 테이블에 저장되었습니다.")
