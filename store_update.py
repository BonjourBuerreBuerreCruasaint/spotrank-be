import mysql.connector
import json
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
store_update_blueprint = Blueprint('store_update', __name__)


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

# 업로드 파일 저장 경로 설정
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}


# 파일 확장자가 허용된 것인지 체크하는 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 가게 정보 수정 API 엔드포인트
@store_update_blueprint.route('/update-store', methods=['POST'])
def update_shop():
    data = request.form
    store_name = data.get('shopName')
    store_phone_number = data.get('shopPhone')
    store_address = data.get('shopAddress')
    store_description = data.get('shopDescription')
    store_images = request.files.getlist('shopImages')

    # 필수 입력값 확인
    if not store_name or not store_phone_number or not store_address or not store_description or len(store_images) == 0:
        return jsonify({"error": "모든 필드를 입력해야 합니다."}), 400

    # 이미지 업로드 처리
    image_paths = []
    for image in store_images:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            image_paths.append(filepath)
        else:
            return jsonify({"error": "허용되지 않는 파일 형식입니다."}), 400

    try:
        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor()

        # JSON으로 이미지 경로 저장
        images_json = json.dumps(image_paths)

        # SQL 업데이트 쿼리
        update_query = """
            UPDATE stores
            SET name = %s, phone = %s, address = %s, description = %s, images = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (store_name, store_phone_number, store_address, store_description, images_json, store_id))
        conn.commit()

        return jsonify({"message": "가게 정보가 수정되었습니다."}), 200

    except mysql.connector.Error as err:
        print(f"데이터베이스 오류: {err}")
        return jsonify({"error": "데이터베이스 오류가 발생했습니다."}), 500

    finally:
        cursor.close()
        conn.close()
app.register_blueprint(store_update_blueprint)

if __name__ == '__main__':
    # 앱 실행
    app.run(debug=True)