import pandas as pd
import mysql.connector

# 데이터베이스 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'welcome1!',
    'database': 'test_db'
}

# CSV 파일 경로
csv_file_path = 'store_info.csv/store_info.csv'

# MySQL에 데이터 삽입 함수
def upload_csv_to_mysql(csv_file_path, db_config, table_name):
    try:
        # 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # CSV 데이터를 DataFrame으로 읽기
        data = pd.read_csv(csv_file_path, low_memory=False)

        # 결측값을 빈 문자열로 대체
        data.fillna(' ', inplace=True)

        # 데이터 타입을 문자열로 명시적으로 변경
        for column in data.columns:
            data[column] = data[column].astype(str)

        # 데이터프레임을 SQL 테이블에 삽입
        for index, row in data.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} ({', '.join(row.index)}) VALUES ({', '.join(['%s'] * len(row))})",
                tuple(row)
            )

        # 변경 사항 커밋
        conn.commit()
        print(f"CSV 파일이 {table_name} 테이블에 성공적으로 업로드되었습니다.")

    except mysql.connector.Error as db_error:
        print(f"데이터베이스 오류: {db_error}")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 예시 사용
table_name = 'store_info'
upload_csv_to_mysql(csv_file_path, db_config, table_name)