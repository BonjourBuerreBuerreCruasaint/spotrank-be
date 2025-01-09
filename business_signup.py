import requests
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
import mysql.connector

# Flask 앱 인스턴스
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

business_join_blueprint = Blueprint('business_join', __name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'y2kxtom16spu!',
    'database': 'info'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"MySQL 연결 실패: {err}")
        raise

# 파일 업로드를 위한 폴더 설정
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 라우팅: 사업자 회원가입
@business_join_blueprint.route('/business-signup', methods=['POST','OPTIONS'])
def business_signup():
    if request.method == 'OPTIONS':
        return '',200

    data = request.form
    file = request.files.get('image')  # 이미지 파일

    business_number = data.get('businessNumber')
    store_name = data.get('storeName')
    address = data.get('address')
    category = data.get('category')
    description = data.get('description')

    if not all([business_number, store_name, address, category]):
        return jsonify({'message':'모든 필드를 입력해야 합니다.'}), 400
    # 파일 저장
    image_filename = None
    if file:
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_filename)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO stores(business_number, store_name, address, category, description, image)
        VALUES(%s, %s, %s, %s, %s, %s)""", (business_number, store_name, address, category, description, image_filename))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': '사업자 정보가 성공적으로 등록되었습니다.'}), 201
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'message':f'사업자 등록 중 오류 발생: {err}'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message':'사업자 등록 중 예기치 않은 오류가 발생했습니다.'}), 500

app.register_blueprint(business_join_blueprint)

if __name__ == '__main__':
    app.run(debug=True)