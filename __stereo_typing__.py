import mysql.connector
import pandas as pd
import math
from datetime import datetime


# MySQL 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'y2kxtom16spu!',
    'database': 'test_db'
}

# MySQL 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'test_db'
}

# 날짜 형식 확인 함수
def is_date(string):
    try:
        datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return True
    except (ValueError, TypeError):
        return False

# NaN 값 확인 함수
def is_nan(value):
    return value is None or (isinstance(value, float) and math.isnan(value))



# MySQL 테이블 생성 함수 (처리된 데이터 저장용)
def create_processed_table():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS processed_orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            store_name VARCHAR(255),
            menu VARCHAR(255),
            price INT,
            order_time DATETIME,
            count INT
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table `processed_orders` is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:

# 데이터베이스에서 모든 `order_` 테이블 이름 가져오기
def get_order_tables():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 모든 테이블 이름 조회
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # `order_`로 시작하는 테이블 필터링
        order_tables = [table[0] for table in tables if table[0].startswith("order_")]

        return order_tables

    except Exception as e:
        print(f"Error fetching table names: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# 특정 테이블 데이터 읽기 및 처리
def process_table_data(table_name):
    combined_data = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 특정 테이블에서 데이터 읽기
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # 데이터프레임으로 변환
        data = pd.DataFrame(rows)

        # 데이터 처리

        for index, row in data.iterrows():
            processed_row = {
                "store_name": row.get("store_name"),
                "menu": None,
                "price": None,
                "order_time": None,
                "count": None,
            }

            try:
                # 모든 열 값을 확인하며 데이터 처리
                for col, value in row.items():  # row.values() 대신 row.items() 사용
                    if isinstance(value, str):
                        if is_date(value):
                            processed_row["order_time"] = value  # 날짜 형식
                        elif processed_row["menu"] is None:
                            processed_row["menu"] = value  # 메뉴
                    elif isinstance(value, (int, float)) and not is_nan(value):
                        if value >= 100 and processed_row["price"] is None:
                            processed_row["price"] = int(value)  # 가격
                        elif processed_row["count"] is None:
                            processed_row["count"] = int(value)  # 수량

                # 누락된 데이터에 기본값 추가
                if processed_row["count"] is None or is_nan(processed_row["count"]):
                    processed_row["count"] = 1  # 기본 수량 값 설정
                if processed_row["price"] is None or is_nan(processed_row["price"]):
                    processed_row["price"] = 0  # 기본 가격 값 설정

                combined_data.append(processed_row)

            except Exception as row_error:
                print(f"Error processing row {index} in table `{table_name}`: {row_error}")

    except Exception as table_error:
        print(f"Error processing table `{table_name}`: {table_error}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return combined_data

# 처리된 데이터를 MySQL에 저장
def save_processed_data_to_mysql(processed_data):
    if not processed_data:
        print("No data to save.")
        return
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 데이터 삽입 쿼리 작성
        insert_query = """
        INSERT INTO processed_orders (store_name, menu, price, order_time, count)
        VALUES (%s, %s, %s, %s, %s)
        """
        for row in processed_data:
            cursor.execute(insert_query, (
                row["store_name"],
                row["menu"],
                row["price"],
                row["order_time"],
                row["count"]
            ))

        conn.commit()
        print(f"Processed data saved to `processed_orders`. Rows inserted: {len(processed_data)}")

    except Exception as e:
        print(f"Error saving to MySQL: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    # 처리된 데이터를 저장할 테이블 생성
    create_processed_table()

    # `order_` 테이블 목록 가져오기
    order_tables = get_order_tables()

    if not order_tables:
        print("No `order_` tables found.")
    else:
        for table_name in order_tables:
            print(f"Processing table: {table_name}")

            # 테이블 데이터 처리
            processed_data = process_table_data(table_name)

            # 처리된 데이터 저장
            save_processed_data_to_mysql(processed_data)
