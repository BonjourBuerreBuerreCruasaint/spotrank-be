import pandas as pd
import random
from datetime import datetime, timedelta
import mysql.connector

# MySQL 데이터베이스 연결
connection = mysql.connector.connect(
    host='15.164.175.70',
    user='root',
    password='Welcome1!',
    database='spotrank'
)

# SQL 쿼리를 사용하여 'stores' 테이블 읽기
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
}


# 랜덤 가격 생성 함수
def random_price():
    return random.randint(5000, 30000)  # 최소 5천원, 최대 3만원


# 랜덤 수량 생성 함수
def random_count():
    return random.randint(1, 30)


# 랜덤 주문 시간 생성 (주 단위)
def random_order_time_weekly():
    now = datetime.now()
    start_week = now - timedelta(days=now.weekday())  # 월요일 기준
    random_days = random.randint(0, 6)  # 7일 중 랜덤 선택
    random_hour = random.randint(6, 23)
    random_minute = random.randint(0, 59)
    return start_week + timedelta(days=random_days, hours=random_hour, minutes=random_minute)


# 랜덤 주문 시간 생성 (월 단위)
def random_order_time_monthly(month_offset):
    now = datetime.now()
    year = now.year + (now.month - 1 + month_offset) // 12
    month = (now.month - 1 + month_offset) % 12 + 1
    start_month = datetime(year, month, 1)
    days_in_month = (start_month.replace(month=month % 12 + 1, day=1) - timedelta(days=1)).day
    random_day = random.randint(1, days_in_month)
    random_hour = random.randint(6, 23)
    return datetime(year, month, random_day, random_hour, random.randint(0, 59))


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

    # 매장 메뉴 확인
    menus = menu_dict.get(sub_category, ["기타 메뉴"])
    if "기타 메뉴" in menus:
        continue  # 기타 메뉴만 있으면 제외

    # 같은 메뉴의 가격을 유지하도록 미리 생성
    menu_price_map = {menu: random_price() for menu in menus}

    # 메뉴 테이블 생성
    menu_table_name = f"menu_{store_id}"
    create_table(cursor, menu_table_name, "menu VARCHAR(255), price INT")

    # 메뉴 데이터 삽입
    menu_data = [(menu, price) for menu, price in menu_price_map.items()]
    insert_data(cursor, menu_table_name, menu_data, ["menu", "price"])

    # 주문 테이블 생성
    order_table_name = f"order_{store_id}"
    create_table(cursor, order_table_name,
                 "store_name VARCHAR(255), menu VARCHAR(255), price INT, order_time DATETIME, count INT")

    # 12개월 데이터 생성
    for month_offset in range(12):
        # 주 단위 데이터 (30개)
        weekly_orders = [
            (store_name, menu, menu_price_map[menu], random_order_time_weekly(), random_count())
            for menu in random.choices(menus, k=30)
        ]
        insert_data(cursor, order_table_name, weekly_orders, ["store_name", "menu", "price", "order_time", "count"])

        # 월 단위 데이터 (30개)
        monthly_orders = [
            (store_name, menu, menu_price_map[menu], random_order_time_monthly(month_offset), random_count())
            for menu in random.choices(menus, k=30)
        ]
        insert_data(cursor, order_table_name, monthly_orders, ["store_name", "menu", "price", "order_time", "count"])

# 커밋 및 종료
connection.commit()
cursor.close()
connection.close()

print("✅ 12개월치 데이터가 성공적으로 생성되었습니다.")