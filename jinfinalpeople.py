from flask import Flask, Blueprint, Response, jsonify
import boto3
import pandas as pd
from flask_cors import CORS
from io import StringIO
import json

app = Flask(__name__)

# CORS 설정: 배포된 프론트엔드의 외부 IP나 도메인으로 변경
CORS(app, resources={r"/api/*": {"origins": "http://spotrank.store"}}, supports_credentials=True)

jinfinalpeople_blueprint = Blueprint('jinfinalpeople', __name__)

# S3에서 CSV 파일을 읽는 함수
def read_csv_from_s3(bucket_name, file_key):
    s3_client = boto3.client('s3')
    try:
        # S3에서 CSV 파일 읽기
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = obj['Body'].read().decode('utf-8')  # 파일 내용 읽기
        return file_content
    except Exception as e:
        print(f"Error reading {file_key} from S3: {e}")
        return None

@jinfinalpeople_blueprint.route('/jinfinalpeople', methods=['GET'])
def serve_jinfinalpeople():
    try:
        # S3에서 CSV 파일을 읽어옵니다.
        csv_data = read_csv_from_s3('backendsource', 'JinFinalPeople.csv')

        if csv_data is None:
            return jsonify({"error": "파일을 S3에서 읽는 중 오류 발생"}), 500

        # CSV 데이터를 DataFrame으로 변환
        df = pd.read_csv(pd.compat.StringIO(csv_data))

        # DataFrame을 원하는 JSON 구조로 변환
        json_data = df.apply(lambda row: {
            "기준_년분기_코드": row['기준_년분기_코드'],  # 컬럼명 그대로 사용
            "상권_구분_코드_명": row['상권_구분_코드_명'],  # 컬럼명 그대로 사용
            "상권배후지_코드_명": row['상권배후지_코드_명'],  # 컬럼명 그대로 사용
            "TotalPeoPle": row['TotalPeoPle'],  # 컬럼명 그대로 사용
            "latitude": row['latitude'],  # 컬럼명 그대로 사용
            "longitude": row['longitude']  # 컬럼명 그대로 사용
        }, axis=1).tolist()  # 각 행을 변환하여 리스트로 반환

        return jsonify(json_data)  # JSON 형식으로 반환
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 오류 발생 시 JSON 형식으로 반환

app.register_blueprint(jinfinalpeople_blueprint)

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True)
