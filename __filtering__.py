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
    password='Welcome1!',  # MySQL 비밀번호

    database='test_db'  # 사용할 데이터베이스 이름
)

# SQL 쿼리를 사용하여 'store_info' 테이블 읽기
query = "SELECT * FROM store_info"

# pandas를 사용하여 SQL 쿼리 결과를 DataFrame으로 변환
df = pd.read_sql(query, connection)

# '상권업종대분류명' 컬럼에서 '식당', '카페', '한식', '음식', '커피'를 포함하는 행만 필터링
filtered_df = df[df['상권업종대분류명'].str.contains('식당|카페|한식|음식|커피', na=False)]

# '시군구명' 컬럼에서 특정 지역(서대문구, 마포구)을 포함하는 행만 필터링
filtered_df = filtered_df[filtered_df['시군구명'].str.contains('서대문구|마포구', na=False)]

# 필요한 컬럼만 선택 (상호명, 상권업종대분류명, 상권업종중분류명, 상권업종소분류명, 시도명, 시군구명, 행정동명, 법정동명, 도로명주소, 경도, 위도)
columns_to_keep = ['상호명', '상권업종대분류명', '상권업종중분류명', '상권업종소분류명',
                   '시도명', '시군구명', '행정동명', '법정동명', '도로명주소', '경도', '위도']
filtered_df = filtered_df[columns_to_keep]

# 필터링된 데이터를 MySQL 테이블에 저장
filtered_table_name = 'filtered_store_info'

# 테이블 생성 쿼리 (필요한 경우에만 실행)
cursor = connection.cursor()
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {filtered_table_name} (

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
    위도 FLOAT
);
"""
cursor.execute(create_table_query)

# DataFrame 데이터를 MySQL 테이블에 삽입
for _, row in filtered_df.iterrows():

    email = fake.email()
    password = fake.password(length=10)
    phone = fake.phone_number()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
    username = fake.user_name()

    insert_query = f"""
    INSERT INTO {filtered_table_name} (상호명, 상권업종대분류명, 상권업종중분류명, 상권업종소분류명, 시도명, 시군구명, 행정동명, 법정동명, 도로명주소, 경도, 위도)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, tuple(row))

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
