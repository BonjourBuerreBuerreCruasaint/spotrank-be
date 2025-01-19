import pandas as pd
import pymysql
from faker import Faker
import random
from datetime import datetime, timedelta
import bcrypt

# Faker 인스턴스 생성
fake = Faker()

# MySQL 데이터베이스 연결
connection = pymysql.connect(
    host='localhost',  # MySQL 호스트
    user='root',  # MySQL 사용자 이름
    password='welcome1!',  # MySQL 비밀번호
    database='test_db'  # 사용할 데이터베이스 이름
)

# SQL 쿼리를 사용하여 'store_info' 테이블 읽기
query = "SELECT * FROM store_info"

# pandas를 사용하여 SQL 쿼리 결과를 DataFrame으로 변환
df = pd.read_sql(query, connection)

# 메뉴 카테고리 딕셔너리
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
# '상권업종대분류명' 컬럼에서 '식당', '카페', '한식', '음식', '커피'를 포함하는 행만 필터링
filtered_df = df[df['상권업종대분류명'].str.contains('식당|카페|한식|음식|커피', na=False)]
# '상권업종소분류명'이 menu_dict에 포함된 데이터 필터링
valid_subcategories = menu_dict.keys()
filtered_df = filtered_df[filtered_df['상권업종소분류명'].isin(valid_subcategories)]
# '시군구명' 컬럼에서 특정 지역(서대문구, 마포구)을 포함하는 행만 필터링
filtered_df = filtered_df[filtered_df['시군구명'].str.contains('서대문구|마포구', na=False)]

# 필요한 컬럼만 선택 (상호명, 상권업종대분류명, 상권업종중분류명, 상권업종소분류명, 시도명, 시군구명, 행정동명, 법정동명, 도로명주소, 경도, 위도)
columns_to_keep = ['상호명', '상권업종소분류명','도로명주소', '경도', '위도']
filtered_df = filtered_df[columns_to_keep].head(5000)

# 필터링된 데이터를 MySQL 테이블에 저장
filtered_table_name = 'stores'

# 테이블 생성 쿼리 (필요한 경우에만 실행)
cursor = connection.cursor()
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {filtered_table_name} (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    상호명 VARCHAR(255),
    상권업종소분류명 VARCHAR(255),
    도로명주소 VARCHAR(255),
    경도 FLOAT,
    위도 FLOAT,
    카테고리 VARCHAR(255),
    가게전화번호 VARCHAR(255),
    개업일 DATE,
    소개글 TEXT,
    이미지 VARCHAR(255)
);
"""
cursor.execute(create_table_query)

# DataFrame 데이터를 MySQL 테이블에 삽입
for _, row in filtered_df.iterrows():
    # 카테고리 설정: 상권업종소분류명이 '카페'인 경우 카테고리='카페', 그렇지 않으면 카테고리='음식점'
    category = '카페' if '카페' in row['상권업종소분류명'] else '음식점'
    # 랜덤 데이터 생성
    store_phone = fake.phone_number()
    open_date = (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime('%Y-%m-%d')
    intro_text = fake.text(max_nb_chars=200)
    image_url = f"https://via.placeholder.com/150?text={fake.word().capitalize()}"
    # Faker 데이터를 생성
    email = fake.email()
    password = bcrypt.hashpw(fake.password(length=10).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    phone = fake.phone_number()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
    username = fake.user_name()

    # 상점 데이터를 삽입
    insert_query = f"""
    INSERT INTO {filtered_table_name} (상호명, 상권업종소분류명, 도로명주소, 경도, 위도, 카테고리, 가게전화번호, 개업일, 소개글, 이미지)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, tuple(row) + (category,store_phone, open_date, intro_text, image_url))

    # 사용자 데이터를 삽입
    insert_user_query = """
        INSERT INTO users (email, password, phone, birthdate, username)
        VALUES (%s, %s, %s, %s, %s)
        """
    cursor.execute(insert_user_query, (email, password, phone, birthdate, username))

# 변경 사항 커밋
connection.commit()

print(f"필터링된 데이터가 MySQL 테이블 '{filtered_table_name}'에 저장되었습니다.")

# 연결 종료
cursor.close()
connection.close()