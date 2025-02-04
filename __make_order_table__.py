import pandas as pd
import random
from datetime import datetime, timedelta
import mysql.connector

# ✅ MySQL 데이터베이스 연결 정보
db_config = {
    'host': '15.164.175.70',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank'
}

# ✅ MySQL 연결
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor(dictionary=True)

# ✅ stores 테이블에서 매장 정보 조회
query = "SELECT id, 상호명, 상권업종소분류명 FROM stores"
cursor.execute(query)
stores = cursor.fetchall()

# ✅ 업종별 메뉴 정의
menu_dict = {
    "빵/도넛": ["크루아상", "도넛", "머핀", "치즈케이크", "타르트"],
    "돼지고기 구이/찜": ["삼겹살", "목살", "항정살", "갈매기살", "보쌈"],
    "요리 주점": ["닭강정", "감자튀김", "떡볶이", "어묵탕", "모듬전"],
    "카페": ["아메리카노", "카푸치노", "케이크", "라떼", "핫초코"],
    "백반/한정식": ["된장찌개", "김치찌개", "제육볶음", "비빔밥", "불고기"],
    "경양식": ["돈가스", "오므라이스", "햄버그스테이크", "카레라이스", "치킨커틀렛"],
    "일식 면 요리": ["라멘", "우동", "소바", "탄탄멘", "니쿠우동"],
    "생맥주 전문": ["IPA", "필스너", "흑맥주", "라거", "에일"],
    "일식 회/초밥": ["연어초밥", "참치회", "광어회", "우니초밥", "장어덮밥"]
}

# ✅ 메뉴별 고정된 가격 설정
menu_price_map = {menu: random.randint(5000, 30000) for sublist in menu_dict.values() for menu in sublist}

# ✅ 2025년 1월 1일부터 12월 31일까지 날짜 생성
def generate_dates():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

# ✅ 랜덤 주문 시간 생성
def random_order_time(base_date):
    return base_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))

# ✅ 랜덤 주문 수량
def random_quantity():
    return random.randint(1, 10)

# ✅ 데이터 삽입 함수 (배치 처리)
def insert_sales_data():
    sales_data = []
    dates = generate_dates()

    # ✅ 각 매장별 데이터 생성
    for store in stores:
        store_id = store["id"]
        store_name = store["상호명"]
        sub_category = store["상권업종소분류명"]

        # ✅ 업종별 메뉴 가져오기
        menus = menu_dict.get(sub_category, ["기타 메뉴"])
        if "기타 메뉴" in menus:
            continue  # 기타 메뉴만 있으면 제외

        # ✅ 모든 날짜와 시간대에 대해 데이터 생성
        for date in dates:
            for _ in range(10):  # 하루에 10건의 주문 생성
                user_id = random.randint(1, 10)  # 랜덤한 user_id
                menu = random.choice(menus)  # 랜덤 메뉴 선택
                price = menu_price_map[menu]  # 같은 메뉴는 동일한 가격 유지
                order_time = random_order_time(date)  # 2025년 특정 날짜의 랜덤 시간
                quantity = random_quantity()  # 랜덤 주문 개수

                sales_data.append((user_id, menu, price, order_time, quantity))

                # ✅ 배치 단위로 MySQL에 데이터 삽입 (1000개씩)
                if len(sales_data) >= 1000:
                    query = """
                        INSERT INTO sales_data (user_id, menu_name, price, order_time, quantity)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.executemany(query, sales_data)
                    connection.commit()
                    sales_data = []  # ✅ 리스트 초기화

    # ✅ 남은 데이터 삽입
    if sales_data:
        query = """
            INSERT INTO sales_data (user_id, menu_name, price, order_time, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(query, sales_data)
        connection.commit()

# ✅ 실행
insert_sales_data()

# ✅ 연결 종료
cursor.close()
connection.close()

print("🎉 2025년 전체 데이터 삽입 완료!")