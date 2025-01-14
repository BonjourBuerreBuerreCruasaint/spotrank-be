from flask import Flask, request, jsonify, session, Blueprint
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pymysql

app = Flask(__name__)
app.secret_key = 'Welcome1!'
store_update_blueprint = Blueprint('store_update_blueprint', __name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# 데이터베이스 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'y2kxtom16spu!',
    'database': 'info'
}

@store_update_blueprint.route('/update-store', methods=['POST'])
def update_store():
    # 세션 확인
    if 'id' not in session:
        return jsonify({'error': '세션에 id가 없습니다.'}), 400

    store_id = session['id']
    print("-----",store_id)
    # 클라이언트에서 전달된 데이터
    store_name = request.form.get('shopName')
    store_phone_number = request.form.get('shopPhone')
    address = request.form.get('shopAddress')
    description = request.form.get('shopDescription')

    shop_images = request.files.getlist('shopImages')

    # 이미지 저장 경로
    image_paths = []
    for image in shop_images:
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_paths.append(image_path)

    # 데이터베이스 업데이트
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 가게 정보 업데이트
            update_query = """
                UPDATE stores
                SET 
                    store_name = %s,
                    store_phone_number = %s,
                    address = %s,
                    description = %s,
                    image = %s
                WHERE id = %s
            """
            image_path = image_paths[0] if image_paths else None  # 첫 번째 이미지를 대표 이미지로 저장
            cursor.execute(update_query, (
                store_name,
                store_phone_number,
                address,
                description,
                image_path,
                store_id
            ))

            connection.commit()

        return jsonify({'message': '가게 정보가 성공적으로 업데이트되었습니다.'}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': '서버에서 문제가 발생했습니다.'}), 500
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)