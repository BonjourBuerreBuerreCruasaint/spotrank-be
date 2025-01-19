import boto3
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
import mysql.connector
import uuid  # 고유 파일 이름 생성을 위한 모듈

# Flask 앱 인스턴스
app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
API_KEY = "650d33464694cb373cf53be21033be2b"

business_join_blueprint = Blueprint('business_join', __name__)

# MySQL 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'welcome1!',
    'database': 'test_db'
}

def get_coordinates_from_address(address):
    """
    도로명 주소를 입력받아 경도와 위도를 반환하는 함수
    :param address: 변환할 도로명 주소 (str)
    :return: 경도와 위도 (tuple) 또는 None
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {API_KEY}",
        "Origin": "http://localhost:3000",  # 정확한 URL과 포트
        "KA": "1"
    }
    params = {
        "query": address
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result["documents"]:
            first_result = result["documents"][0]
            longitude = float(first_result["x"])  # 경도
            latitude = float(first_result["y"])  # 위도
            return longitude, latitude
        else:
            print("해당 주소에 대한 결과를 찾을 수 없습니다.")
            return None
    else:
        print(f"API 요청 실패: {response.status_code}, {response.text}")
        return None

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"MySQL 연결 실패: {err}")
        raise

# 라우팅: 사업자 회원가입
@business_join_blueprint.route('/business-signup', methods=['POST', 'OPTIONS'])
def business_signup():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.form
    file = request.files.get('image')  # 이미지 파일

    business_number = data.get('businessNumber')
    store_name = data.get('storeName')
    address = data.get('address')
    category = data.get('category')
    sub_category = data.get('subCategory')  # 추가된 필드
    description = data.get('description')
    opening_date = data.get('openingDate')
    store_phone_number = data.get('storePhoneNumber')

    coordinate = get_coordinates_from_address(address)

    if not all([business_number, store_name, address, category]):
        return jsonify({'message': '모든 필드를 입력해야 합니다.'}), 400

    if coordinate is None:
        return jsonify({'message': '유효한 주소가 아닙니다.'}), 400

    # 파일 저장
    image_filename = None
    if file:
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_filename)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # users 테이블에서 userId 가져오기
        user_email = data.get('userEmail')  # 사용자 이메일 (추가됨)
        user_id = get_user_id_by_email(cursor, user_email)
        if not user_id:
            return jsonify({'message': '해당 이메일로 등록된 사용자가 없습니다.'}), 404

        # S3에 파일 업로드
        image_url = None
        if file:
            unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                unique_filename,
                ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
            )
            image_url = f"{S3_LOCATION}{unique_filename}"

        # 사업자 정보 삽입
        cursor.execute("""
        INSERT INTO stores(user_id, business_number, store_name, address, category, description, image_url, store_phone_number)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""",
                       (user_id, business_number, store_name, address, category, description, image_url, store_phone_number))

        connection.commit()

        # 삽입된 사업자의 ID 가져오기 (Auto Increment된 PK)
        store_id = cursor.lastrowid

        # 동적 테이블 생성
        create_dynamic_tables(cursor, store_id)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': '사업자 정보가 성공적으로 등록되었습니다.'}), 201
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'message': f'사업자 등록 중 오류 발생: {err}'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': '사업자 등록 중 예기치 않은 오류가 발생했습니다.'}), 500

app.register_blueprint(business_join_blueprint)

if __name__ == '__main__':
    app.run(debug=True)