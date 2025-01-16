import pandas as pd
import random
from datetime import datetime, timedelta
import mysql.connector
import re

# MySQL 데이터베이스 연결
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='y2kxtom16spu!',
    database='test_db'
)

# SQL 쿼리를 사용하여 'filtered_store_info' 테이블 읽기
query = """
    SELECT id, 상호명, 상권업종소분류명 
    FROM filtered_store_info 
"""
data = pd.read_sql(query, connection)

# 업종 소분류별 메뉴 목록 정의
menu_dict = {
    "일식 면 요리": ["라멘", "우동", "소바", "탄탄멘"],
    "카페": ["아메리카노", "카푸치노", "케이크", "라떼", "핫초코"],
    "생맥주 전문": ["IPA", "필스너", "흑맥주", "라거", "에일"],
    "요리 주점": ["닭강정", "감자튀김", "떡볶이", "어묵탕", "모듬전"],
    "일식 회/초밥": ["연어초밥", "참치회", "광어회", "우니초밥", "장어덮밥"],
    "김밥/만두/분식": ["김밥", "떡볶이", "만두", "순대", "튀김"],
    "빵/도넛": ["크루아상", "도넛", "머핀", "치즈케이크", "타르트"],
    "한식": ["된장찌개", "김치찌개", "제육볶음", "비빔밥", "불고기"],
    "중식": ["짜장면", "짬뽕", "탕수육", "마라탕", "깐풍기"],
    "양식": ["스테이크", "파스타", "피자", "샐러드", "리조또"],
    "패스트푸드": ["햄버거", "치킨너겟", "프렌치프라이", "핫도그", "콜라"],
    "아이스크림/디저트": ["아이스크림", "와플", "빙수", "마카롱", "쿠키"],
    "피자 전문점": ["마르게리타", "고르곤졸라", "불고기피자", "포테이토피자", "콤비네이션"],
    "치킨 전문점": ["후라이드치킨", "양념치킨", "간장치킨", "마늘치킨", "허니콤보"],
    "족발/보쌈": ["족발", "보쌈", "쟁반국수", "막국수", "김치전"],
    "샌드위치/샐러드": ["치킨샐러드", "에그샌드위치", "BLT샌드위치", "클럽샌드위치", "과일샐러드"],
    "해산물": ["조개찜", "문어숙회", "낙지볶음", "해물파전", "바지락칼국수"],
    "베이커리": ["바게트", "스콘", "브리오슈", "파네토네", "체다치즈빵"],
    "뷔페": ["초밥", "스테이크", "탕수육", "피자", "샐러드"],
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

print("모든 메뉴 및 주문 데이터가 생성되었습니다.")