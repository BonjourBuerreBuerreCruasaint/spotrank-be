from flask import Flask, jsonify, Blueprint
import boto3
from io import StringIO
from flask_cors import CORS

app = Flask(__name__)

# CORS 설정: 배포된 프론트엔드의 외부 IP나 도메인으로 변경
CORS(app, resources={r"/api/*": {"origins": "http://a06c35398b3554cde90a91e66318d385-363860986.ap-northeast-2.elb.amazonaws.com"}}, supports_credentials=True)

jinfinalpeople_blueprint = Blueprint('jinfinalpeople', __name__)

# S3에서 파일을 읽는 함수
def read_csv_from_s3(bucket_name, file_key):
    s3_client = boto3.client('s3')
    try:
        # S3에서 파일 읽기
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = obj['Body'].read().decode('utf-8')  # 파일 내용 읽기
        return file_content
    except Exception as e:
        print(f"Error reading {file_key} from S3: {e}")
        return None

@jinfinalpeople_blueprint.route('/jinfinalpeople', methods=['GET'])
def serve_jinfinalpeople():
    try:
        # S3에서 JinFinalPeople.csv 파일을 읽어옵니다.
        file_content = read_csv_from_s3('backendsource', 'JinFinalPeople.csv')

        if file_content is None:
            return jsonify({"error": "파일을 S3에서 읽는 중 오류 발생"}), 500

        # CSV 내용을 줄 단위로 나누기
        data = file_content.splitlines()

        return jsonify({"content": data})  # CSV 데이터 반환

    except Exception as e:
        # 오류 처리
        return jsonify({"error": "CSV 파일을 제공하는 중 오류 발생", "details": str(e)}), 500

app.register_blueprint(jinfinalpeople_blueprint)

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True)
