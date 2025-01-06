import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)

# MySQL 데이터베이스 연결 정보
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'test_db'
}

def get_db_connection():
    """MySQL 데이터베이스 연결"""
    try:
        return pymysql.connect(**db_config)
    except pymysql.MySQLError as err:
        print(f"MySQL 연결 실패: {err}")
        raise

def create_sales_table_for_store(store_id):
    """새로운 매장을 위한 실시간 매출정보 테이블 생성"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 동적으로 테이블 생성
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS Sales_{store_id} (
                sales_ID INT AUTO_INCREMENT PRIMARY KEY,
                store_ID INT NOT NULL,
                user_ID INT NOT NULL,
                timestamp DATETIME NOT NULL,
                menu VARCHAR(255),
                quantity INT DEFAULT 0,
                revenue DECIMAL(10, 2) DEFAULT 0.00,
                FOREIGN KEY (store_ID) REFERENCES Store(store_ID),
                FOREIGN KEY (user_ID) REFERENCES User(user_ID)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_query)
            connection.commit()
            print(f"Sales_{store_id} 테이블이 성공적으로 생성되었습니다.")
    except pymysql.MySQLError as err:
        print(f"테이블 생성 중 오류 발생: {err}")
    finally:
        if connection:
            connection.close()

@app.route('/')
def home():
    """루트 경로"""
    return "Flask 애플리케이션이 정상적으로 실행 중입니다!"

@app.route('/add_store', methods=['POST'])
def add_store():
    """새로운 매장을 추가하고 실시간 매출정보 테이블 생성"""
    data = request.json
    user_id = data.get('user_id')
    store_name = data.get('store_name')
    address = data.get('address')
    store_number = data.get('store_number')
    category = data.get('category')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([user_id, store_name, address, category, latitude, longitude]):
        return jsonify({'message': '모든 필드를 입력해야 합니다.'}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 새로운 매장 추가
            insert_store_query = """
            INSERT INTO Store (user_ID, store_name, address, store_number, category, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_store_query, (user_id, store_name, address, store_number, category, latitude, longitude))
            connection.commit()

            # 새로 추가된 매장의 ID 가져오기
            store_id = cursor.lastrowid

        # 실시간 매출정보 테이블 생성
        create_sales_table_for_store(store_id)

        return jsonify({'message': f'매장 {store_name}이 성공적으로 추가되었습니다.', 'store_id': store_id}), 201

    except pymysql.MySQLError as err:
        return jsonify({'message': f'매장 추가 중 오류 발생: {err}'}), 500

    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
def create_analysis_and_visualization_tables(store_id):
    """메뉴 분석 및 시각화 데이터를 위한 테이블 생성"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 메뉴 분석 테이블 생성
            create_menu_analysis_query = f"""
            CREATE TABLE IF NOT EXISTS MenuAnalysis_{store_id} (
                menu VARCHAR(255) NOT NULL,
                total_quantity INT DEFAULT 0,
                total_revenue DECIMAL(10, 2) DEFAULT 0.00,
                PRIMARY KEY (menu)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_menu_analysis_query)

            # 시각화 데이터 테이블 생성
            create_visualization_query = f"""
            CREATE TABLE IF NOT EXISTS Visualization_{store_id} (
                timestamp DATETIME NOT NULL,
                hourly_sales DECIMAL(10, 2) DEFAULT 0.00,
                top_menu VARCHAR(255),
                PRIMARY KEY (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_visualization_query)

        connection.commit()
        print(f"MenuAnalysis_{store_id} 및 Visualization_{store_id} 테이블이 성공적으로 생성되었습니다.")
    except pymysql.MySQLError as err:
        print(f"테이블 생성 중 오류 발생: {err}")
    finally:
        if connection:
            connection.close()


@app.route('/add_store', methods=['POST'])
def add_store():
    """새로운 매장을 추가하고 관련 테이블 생성"""
    data = request.json
    user_id = data.get('user_id')
    store_name = data.get('store_name')
    address = data.get('address')
    store_number = data.get('store_number')
    category = data.get('category')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([user_id, store_name, address, category, latitude, longitude]):
        return jsonify({'message': '모든 필드를 입력해야 합니다.'}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 새로운 매장 추가
            insert_store_query = """
            INSERT INTO Store (user_ID, store_name, address, store_number, category, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_store_query, (user_id, store_name, address, store_number, category, latitude, longitude))
            connection.commit()

            # 새로 추가된 매장의 ID 가져오기
            store_id = cursor.lastrowid

        # 실시간 매출정보 테이블 생성
        create_sales_table_for_store(store_id)

        # 메뉴 분석 및 시각화 데이터 테이블 생성
        create_analysis_and_visualization_tables(store_id)

        return jsonify({'message': f'매장 {store_name}이 성공적으로 추가되었습니다.', 'store_id': store_id}), 201

    except pymysql.MySQLError as err:
        return jsonify({'message': f'매장 추가 중 오류 발생: {err}'}), 500

    finally:
        if connection:
            connection.close()