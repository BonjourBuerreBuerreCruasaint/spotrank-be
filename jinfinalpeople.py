from flask import Flask, Blueprint, Response
import boto3
import pandas as pd
from flask_cors import CORS
from io import StringIO
import json

app = Flask(__name__)

# CORS 설정: 배포된 프론트엔드의 외부 IP나 도메인으로 변경
CORS(app, resources={r"/api/*": {"origins": "http://a394d93e1cb164bc48aee934560371a1-1195758023.ap-northeast-2.elb.amazonaws.com"}}, supports_credentials=True)

jinfinalpeople_blueprint = Blueprint('jinfinalpeople', __name__)

# S3에서 CSV 파일을 읽는 함수
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
            error_response = {"error": "파일을 S3에서 읽는 중 오류 발생"}
            return Response(
                response=json.dumps(error_response, ensure_ascii=False),
                mimetype='application/json',
                status=500,
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )

        # pandas로 CSV 내용을 DataFrame으로 변환하여 JSON으로 반환
        csv_buffer = StringIO(file_content)
        df = pd.read_csv(csv_buffer)
        # DataFrame을 JSON으로 변환
        json_data = df.to_dict(orient='records')  # 'records' 형식으로 변환하여 리스트로 반환

        # 유효한 데이터를 JSON 형식으로 반환
        return Response(
            response=json.dumps({"content": json_data}, ensure_ascii=False),
            mimetype='application/json',
            status=200,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )

    except Exception as e:
        # 오류 처리
        error_response = {
            "error": "CSV 파일을 제공하는 중 오류 발생",
            "details": str(e)
        }
        return Response(
            response=json.dumps(error_response, ensure_ascii=False),
            mimetype='application/json',
            status=500,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )

app.register_blueprint(jinfinalpeople_blueprint)

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True)
