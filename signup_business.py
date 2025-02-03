import boto3
import requests
import os
import mysql.connector
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# 환경 변수 로드
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "default_key_if_missing")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "default_secret_if_missing")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "default_bucket_if_missing")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")  # 기본값 설정

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

API_KEY = "650d33464694cb373cf53be21033be2b"
business_join_blueprint = Blueprint('business_join', __name__)

# MySQL 설정
db_config = {
    'host': '15.164.175.70',
    'user': 'root',
    'password': 'Welcome1!',
    'database': 'spotrank'

}

def get_coordinates_from_address(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {API_KEY}",
        "Origin": "http://localhost:3000",
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
            latitude = float(first_result["y"])   # 위도
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

@business_join_blueprint.route('/business-signup', methods=['POST', 'OPTIONS'])
def business_signup():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.form
    file = request.files.get('image')  # 이미지 파일 저장 url

    business_number = data.get('businessNumber')
    store_name = data.get('storeName')
    address = data.get('address')
    category = data.get('category')
    sub_category = data.get('subCategory')
    description = data.get('description')
    opening_date = data.get('openingDate')
    store_phone_number = data.get('storePhoneNumber')

    coordinate = get_coordinates_from_address(address)
    if not all([business_number, store_name, address, category]):
        return jsonify({'message': '모든 필드를 입력해야 합니다.'}), 400

    if coordinate is None:
        return jsonify({'message': '유효한 주소가 아닙니다.'}), 400

    # 파일을 S3에 업로드
    image_filename = None
    if file:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        filename = secure_filename(file.filename)  # 안전한 파일 이름 생성

        try:
            # 파일을 S3 버킷에 업로드
            s3.upload_fileobj(
                file,
                AWS_BUCKET_NAME,
                filename,
                ExtraArgs={
                    "ContentType": file.content_type
                }
            )

            # 업로드된 파일의 접속 가능한 URL
            image_filename = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        except Exception as e:
            print(f"S3 업로드 실패: {e}")
            return jsonify({'message': f'이미지 업로드 중 오류 발생: {e}'}), 500

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO stores(상호명, 도로명주소, 카테고리, 상권업종소분류명, 경도, 위도, 소개글, 이미지, 개업일, 가게전화번호)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            store_name,
            address,
            category,
            sub_category,
            coordinate[0],
            coordinate[1],
            description,
            image_filename,
            opening_date,
            store_phone_number
        ))

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
    app.run(debug=True, host='0.0.0.0', port=5000)