import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'test_db'
}

try:
    connection = mysql.connector.connect(**db_config)
    print("MySQL 연결 성공!")
    connection.close()
except mysql.connector.Error as err:
    print(f"MySQL 연결 실패: {err}")

