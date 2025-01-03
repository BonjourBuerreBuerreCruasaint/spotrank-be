from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Flask 앱 인스턴스
app = Flask(__name__)

# CORS 설정
CORS(app)

# MySQL 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+mysqlconnector://root:y2kxtom16spu!@localhost/info"  # 사용자 설정 필요
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 파일 업로드를 위한 폴더 설정
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 데이터베이스 객체
db = SQLAlchemy(app)

# 데이터베이스 모델
class Business(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_number = db.Column(db.String(20), unique=True, nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

# 라우팅: 사업자 회원가입
@app.route('/api/business-signup', methods=['POST'])
def business_signup():
    data = request.form
    file = request.files.get('image')  # 이미지 파일

    business_number = data.get('businessNumber')
    store_name = data.get('storeName')
    address = data.get('address')
    category = data.get('category')
    description = data.get('description')

    # 파일 저장
    image_filename = None
    if file:
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_filename)

    # 데이터베이스에 사업자 정보 저장
    new_business = Business(
        business_number=business_number,
        store_name=store_name,
        address=address,
        category=category,
        description=description,
        image=image_filename
    )

    try:
        db.session.add(new_business)
        db.session.commit()
        return jsonify({"message": "Business registration successful!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)