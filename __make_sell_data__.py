import random
import threading
from flask import Flask, jsonify, Blueprint
from datetime import datetime
import mysql.connector

make_sell_data_blueprint = Blueprint('make_sell_data', __name__)

# 데이터베이스 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'welcome1!',
    'database': 'test_db',
    'auth_plugin': 'mysql_native_password'

}


# MySQL 테이블 생성 함수
def create_sales_table():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # sales_data 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sales_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            menu_name VARCHAR(255),
            price DECIMAL(10, 2),
            order_time DATETIME,
            quantity INT
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table `sales_data` is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# 모든 order_* 테이블을 sales_data 테이블로 합치는 함수
def merge_order_tables():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # order_* 테이블 이름 가져오기
        cursor.execute("SHOW TABLES WHERE Tables_in_test_db LIKE 'order_%'")
        order_tables = [row[0] for row in cursor.fetchall()]

        if not order_tables:
            print("No order tables found.")
            return

        # 각 order 테이블 데이터를 sales_data에 삽입
        for table_name in order_tables:
            # user_id는 테이블 이름에서 추출
            user_id = int(table_name.split('_')[1])

            # order_* 테이블의 데이터 가져오기
            select_query = f"SELECT menu, price, order_time, count FROM {table_name}"
            cursor.execute(select_query)
            orders = cursor.fetchall()

            # sales_data 테이블에 삽입
            insert_query = """
                INSERT INTO sales_data (user_id, menu_name, price, order_time, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """
            sales_data = [
                (user_id, row[0], row[1], row[2], row[3]) for row in orders
            ]
            cursor.executemany(insert_query, sales_data)
            conn.commit()
            print(f"Data from {table_name} merged into sales_data.")
    except Exception as e:
        print(f"Error merging order tables: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask 애플리케이션 설정
app = Flask(__name__)
app.register_blueprint(make_sell_data_blueprint)

@app.route('/merge', methods=['GET'])
def merge_tables_endpoint():
    merge_order_tables()
    return jsonify({"message": "All order_* tables merged into sales_data."})

if __name__ == "__main__":

    # sales_data 테이블 생성
    create_sales_table()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)