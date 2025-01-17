import pandas as pd
import pymysql
from faker import Faker
import bcrypt

# Faker 인스턴스 생성
fake = Faker()

# MySQL 데이터베이스 연결 (pymysql 사용)
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='welcome1!',
    database='test_db',
    charset='utf8mb4'
)

# 'store_info' 테이블에서 데이터 읽기
query = "SELECT * FROM store_info"
df = pd.read_sql(query, con=connection)

# '상권업종대분류명' 필터링
filtered_df = df[df['상권업종대분류명'].str.contains('식당|카페|한식|음식|커피', na=False)]

# '시군구명' 필터링
filtered_df = filtered_df[filtered_df['시군구명'].str.contains('서대문구|마포구', na=False)]

# 필요한 컬럼만 선택
columns_to_keep = ['상호명', '상권업종대분류명', '상권업종중분류명', '상권업종소분류명',
                   '시도명', '시군구명', '행정동명', '법정동명', '도로명주소', '경도', '위도']
filtered_df = filtered_df[columns_to_keep]

# 카테고리 설정
filtered_df['카테고리'] = filtered_df['상권업종소분류명'].fillna('').apply(
    lambda x: '카페' if '카페' in x else '음식점'
)

cursor = connection.cursor()

# 테이블 생성 쿼리
create_table_query = """
CREATE TABLE IF NOT EXISTS filtered_store_info (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    상호명 VARCHAR(255),
    상권업종대분류명 VARCHAR(255),
    상권업종중분류명 VARCHAR(255),
    상권업종소분류명 VARCHAR(255),
    시도명 VARCHAR(255),
    시군구명 VARCHAR(255),
    행정동명 VARCHAR(255),
    법정동명 VARCHAR(255),
    도로명주소 VARCHAR(255),
    경도 FLOAT,
    위도 FLOAT,
    카테고리 VARCHAR(255)
);
"""
cursor.execute(create_table_query)

# 데이터 삽입
for _, row in filtered_df.iterrows():
    # 각 값들을 튜플로 변환
    row_values = (
        row['상호명'], row['상권업종대분류명'], row['상권업종중분류명'],
        row['상권업종소분류명'], row['시도명'], row['시군구명'],
        row['행정동명'], row['법정동명'], row['도로명주소'],
        row['경도'], row['위도'], row['카테고리']
    )

    # 상점 데이터 삽입
    insert_query = """
    INSERT INTO filtered_store_info (상호명, 상권업종대분류명, 상권업종중분류명, 상권업종소분류명, 
                                     시도명, 시군구명, 행정동명, 법정동명, 도로명주소, 경도, 위도, 카테고리)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, row_values)
    print(f"상호명: {row['상호명']}, 카테고리: {row['카테고리']}가 filtered_store_info에 삽입되었습니다.")

    # 사용자 데이터 생성
    email = fake.email()
    password = bcrypt.hashpw(fake.password(length=10).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    phone = fake.phone_number()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
    username = fake.user_name()

    # 사용자 데이터 삽입
    insert_user_query = """
        INSERT INTO users (email, password, phone, birthdate, username)
        VALUES (%s, %s, %s, %s, %s)
        """
    cursor.execute(insert_user_query, (email, password, phone, birthdate, username))
    print(f"사용자 이메일: {email}, 사용자 이름: {username}가 users에 삽입되었습니다.")

# 변경 사항 커밋
connection.commit()
print(f"필터링된 데이터가 MySQL 테이블 'filtered_store_info'에 저장되었습니다.")

# 연결 종료
cursor.close()
connection.close()