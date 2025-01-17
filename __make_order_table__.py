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
    return int(random.randint(10, 500) * 100)

# 랜덤 수량 생성 함수
def random_count():
    return random.randint(1, 30)

# 랜덤 주문 시간 생성 함수
def random_order_time():
    now = datetime.now()

    random_days = random.randint(0, 365)
    random_minutes = random.randint(0, 1440)
    random_date = now - timedelta(days=random_days, minutes=random_minutes)
    return random_date

# 테이블 생성 함수
def create_table(cursor, table_name, schema):
    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
    cursor.execute(create_query)

# 데이터 삽입 함수
def insert_data(cursor, table_name, data, columns):
    placeholders = ', '.join(['%s'] * len(columns))
    columns_joined = ', '.join(columns)
    query = f"INSERT INTO {table_name} ({columns_joined}) VALUES ({placeholders})"
    cursor.executemany(query, data)

# MySQL 작업 시작
cursor = connection.cursor()

# 각 ID에 대해 테이블 생성 및 데이터 삽입
for _, row in data.iterrows():
    store_id = row["id"]
    store_name = row["상호명"]
    sub_category = row["상권업종소분류명"]

    # 메뉴 테이블 및 데이터 생성
    menu_table_name = f"menu_{store_id}"
    menu_schema = "menu VARCHAR(255), price INT"
    create_table(cursor, menu_table_name, menu_schema)

    menus = menu_dict.get(sub_category, ["기타 메뉴"])
    if "기타 메뉴" in menus:
        continue  # 기타 메뉴만 있는 경우 건너뜀

    menu_data = [(menu, random_price()) for menu in menus]
    insert_data(cursor, menu_table_name, menu_data, ["menu", "price"])

    # 주문 테이블 및 데이터 생성
    order_table_name = f"order_{store_id}"
    order_schema = "menu VARCHAR(255), price INT, order_time DATETIME, count INT"
    create_table(cursor, order_table_name, order_schema)

    order_data = [
        (random.choice(menus), random_price(), random_order_time(), random_count())
        for _ in range(100)
    ]
    insert_data(cursor, order_table_name, order_data, ["menu", "price", "order_time", "count"])

# 변경 사항 커밋 및 연결 종료
connection.commit()
cursor.close()
connection.close()


print(f"메뉴 및 주문 데이터가 '{menu_table_name}'와 '{order_table_name}' 테이블에 저장되었습니다.")
