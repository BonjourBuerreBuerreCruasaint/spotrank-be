import pandas as pd
import random
from datetime import datetime, timedelta
import mysql.connector
import re

# MySQL 데이터베이스 연결
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='welcome1!',
    database='test_db'

)

# SQL 쿼리를 사용하여 'filtered_store_info' 테이블 읽기
query = "SELECT * FROM stores"


data = pd.read_sql(query, connection)

# 업종 소분류별 메뉴 목록 정의
menu_dict = {
    "빵/도넛": ["크루아상", "도넛", "머핀", "치즈케이크", "타르트"],
    "돼지고기 구이/찜": ["삼겹살", "목살", "항정살", "갈매기살", "보쌈"],
    "요리 주점": ["닭강정", "감자튀김", "떡볶이", "어묵탕", "모듬전"],
    "카페": ["아메리카노", "카푸치노", "케이크", "라떼", "핫초코"],
    "백반/한정식": ["된장찌개", "김치찌개", "제육볶음", "비빔밥", "불고기"],
    "경양식": ["돈가스", "오므라이스", "햄버그스테이크", "카레라이스", "치킨커틀렛"],
    "일식 면 요리": ["라멘", "우동", "소바", "탄탄멘", "니쿠우동"],
    "생맥주 전문": ["IPA", "필스너", "흑맥주", "라거", "에일"],
    "일식 회/초밥": ["연어초밥", "참치회", "광어회", "우니초밥", "장어덮밥"],
    "피자": ["마르게리타", "고르곤졸라", "불고기피자", "포테이토피자", "콤비네이션"],
    "파스타/스테이크": ["카르보나라", "알리오올리오", "리조또", "티본스테이크", "안심스테이크"],
    "김밥/만두/분식": ["김밥", "떡볶이", "만두", "순대", "튀김"],
    "치킨": ["후라이드치킨", "양념치킨", "간장치킨", "마늘치킨", "허니콤보"],
    "국/탕/찌개류": ["갈비탕", "설렁탕", "감자탕", "된장찌개", "육개장"],
    "국수/칼국수": ["잔치국수", "바지락칼국수", "메밀국수", "소고기국수", "비빔국수"],
    "버거": ["치즈버거", "불고기버거", "더블패티버거", "베이컨치즈버거", "치킨버거"],
    "중국집": ["짜장면", "짬뽕", "탕수육", "깐풍기", "마파두부"],
    "일식 카레/돈가스/덮밥": ["가츠동", "카레라이스", "규동", "텐동", "에비동"],
    "마라탕/훠궈": ["마라탕", "마라샹궈", "훠궈", "우삼겹훠궈", "마라룽샤"],
    "닭/오리고기 구이/찜": ["닭갈비", "오리훈제", "찜닭", "닭볶음탕", "간장찜닭"],
}

# 랜덤 가격 생성 함수
def random_price():
    return random.randint(1000, 50000)

# 랜덤 수량 생성 함수
def random_count():
    return random.randint(1, 30)

# 랜덤 주문 시간 생성 (주 단위)
def random_order_time_weekly():
    now = datetime.now()
    start_week = now - timedelta(days=now.weekday())  # 월요일 기준
    random_days = random.randint(0, 6)  # 7일 중 랜덤 선택
    random_hour = random.randint(6, 23)  # 6시 ~ 23시
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return start_week + timedelta(days=random_days, hours=random_hour, minutes=random_minute, seconds=random_second)

# 랜덤 주문 시간 생성 (월 단위)
def random_order_time_monthly(month_offset):
    now = datetime.now()
    year = now.year + (now.month - 1 + month_offset) // 12
    month = (now.month - 1 + month_offset) % 12 + 1
    start_month = datetime(year, month, 1)
    days_in_month = (start_month.replace(month=month % 12 + 1, day=1) - timedelta(days=1)).day
    random_day = random.randint(1, days_in_month)
    random_hour = random.randint(6, 23)  # 6시 ~ 23시
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return datetime(year, month, random_day, random_hour, random_minute, random_second)

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

# MySQL 작업
cursor = connection.cursor()

for _, row in data.iterrows():
    store_id = row["id"]
    store_name = row["상호명"]
    sub_category = row["상권업종소분류명"]

    # 메뉴 테이블 생성
    menu_table_name = f"menu_{store_id}"
    create_table(cursor, menu_table_name, "menu VARCHAR(255), price INT")
    menus = menu_dict.get(sub_category, ["기타 메뉴"])
    if "기타 메뉴" in menus:
        continue

    menu_data = [(menu, random_price()) for menu in menus]
    menu_price_map = {menu: price for menu, price in menu_data}
    insert_data(cursor, menu_table_name, menu_data, ["menu", "price"])

    # 주문 테이블 생성
    order_table_name = f"order_{store_id}"
    create_table(cursor, order_table_name, "menu VARCHAR(255), price INT, order_time DATETIME, count INT")

    # 12개월 데이터 생성
    for month_offset in range(12):
        # 주 단위 데이터 (30개)
        weekly_orders = [
            (menu, menu_price_map[menu], random_order_time_weekly(), random_count())
            for menu in random.choices(menus, k=30)
        ]
        insert_data(cursor, order_table_name, weekly_orders, ["menu", "price", "order_time", "count"])

        # 월 단위 데이터 (30개)
        monthly_orders = [
            (menu, menu_price_map[menu], random_order_time_monthly(month_offset), random_count())
            for menu in random.choices(menus, k=30)
        ]
        insert_data(cursor, order_table_name, monthly_orders, ["menu", "price", "order_time", "count"])

# 커밋 및 종료
connection.commit()
cursor.close()
connection.close()

print("12개월치 데이터가 성공적으로 생성되었습니다.")