import mysql.connector
from datetime import datetime

# ✅ MySQL 연결 정보
db_config = {
    'host': '15.164.175.70',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank'
}

def get_db_connection():
    """ MySQL 데이터베이스 연결 """
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("✅ MySQL 연결 성공")
            return conn
    except mysql.connector.Error as err:
        print(f"🚨 MySQL 연결 실패: {err}")
    return None

def insert_ranking_data():
    """ sales_data에서 오늘의 매출 데이터를 가져와 ranking 테이블에 저장 """
    conn = None
    try:
        # ✅ MySQL 연결
        conn = get_db_connection()
        if not conn:
            print("❌ MySQL 연결을 가져오지 못했습니다.")
            return

        # ✅ 새로운 연결을 강제로 설정하여 기존 연결 문제 방지
        conn.ping(reconnect=True)

        print("🔥 오늘의 매출 데이터를 조회 중...")

        with conn.cursor(dictionary=True) as cursor:
            # ✅ sales_data와 stores를 JOIN하여 상호명(store_name) 가져오기
            query = """
                SELECT 
                    s.상호명 AS store_name,
                    s.상권업종소분류명 AS category,
                    SUM(sd.quantity) AS total_quantity
                FROM sales_data sd
                JOIN stores s ON sd.user_id = s.id
                WHERE DATE(sd.order_time) = CURDATE()
                GROUP BY s.상호명, s.상권업종소분류명
                ORDER BY total_quantity DESC
                LIMIT 30;
            """
            cursor.execute(query)
            sales_results = cursor.fetchall()

        if not sales_results:
            print("❌ 오늘의 매출 데이터가 없습니다.")
            return

        print("✅ 랭킹 데이터 저장 중...")

        # ✅ 새로운 커서로 INSERT 실행 (트랜잭션을 별도로 관리)
        with conn.cursor() as insert_cursor:
            insert_query = """
                INSERT INTO ranking (shop_name, category, quantity, order_time)
                VALUES (%s, %s, %s, NOW())
            """
            insert_cursor.executemany(insert_query, [(row["store_name"], row["category"], row["total_quantity"]) for row in sales_results])

        # ✅ 트랜잭션 커밋
        conn.commit()
        print("🎉 랭킹 데이터 삽입 완료!")

    except mysql.connector.Error as err:
        if conn and conn.is_connected():
            conn.rollback()  # 🚨 에러 발생 시 롤백
        print(f"🚨 MySQL 오류 발생: {err}")

    finally:
        if conn and conn.is_connected():
            conn.close()
            print("✅ MySQL 연결이 정상적으로 종료되었습니다.")

# ✅ 실행
insert_ranking_data()