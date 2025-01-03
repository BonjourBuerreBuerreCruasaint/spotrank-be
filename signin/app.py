import mysql.connector
from mysql.connector import Error
import bcrypt

# 데이터베이스 연결 함수
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',          # 로컬 호스트
            database='spotrank_db',      # 데이터베이스 이름
            user='root',           # MySQL 사용자 이름
            password='Welcome1!'        # MySQL 비밀번호
        )
        if connection.is_connected():
            print("Connected to the database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


# 사용자 정보 삽입 함수
def insert_user(connection, name, email, password, phone_number):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO users (name, email, password, phone_number) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, password, phone_number))
        connection.commit()  # 변경사항 저장
        print("User information saved successfully!")
    except Error as e:
        if "Duplicate entry" in str(e):
            print("Error: The email already exists in the database.")
        else:
            print(f"Error: {e}")

# 메인 함수
def main():
    # 데이터베이스 연결 생성
    connection = create_connection()
    if connection is None:
        return

# 비밀번호 해싱 함수
    def hash_password(password):
        salt = bcrypt.gensalt()  # 솔트 생성
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')  # 문자열로 변환

    # 사용자 입력 받기
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    phone_number = input("Enter your phone number: ")

    # 사용자 정보 삽입
    insert_user(connection, name, email, password, phone_number)

    # 연결 종료
    connection.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()