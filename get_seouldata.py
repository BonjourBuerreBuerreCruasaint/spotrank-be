from flask import Flask, jsonify, Blueprint
import os
import json
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

get_seouldata_blueprint = Blueprint('get_seouldata', __name__)

@get_seouldata_blueprint.route('/seouldata', methods=['GET'])
def serve_seouldata():
    try:
        # 현재 파일의 디렉토리 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'modified_file.json')

        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            return jsonify({"error": "파일이 존재하지 않습니다."}), 404

        # JSON 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # JSON 파일을 파싱

        # 데이터 검증: latitude, longitude 값 확인
        invalid_entries = []
        for index, entry in enumerate(data):
            latitude = entry.get("latitude")
            longitude = entry.get("longitude")
            if latitude is None or longitude is None:
                invalid_entries.append(index)

        # 유효하지 않은 항목 로그 출력
        # if invalid_entries:
        #     print(f"유효하지 않은 항목 발견: {len(invalid_entries)}개")
        #     for idx in invalid_entries:
        #         print(f" - Index {idx}: {data[idx]}")

        return jsonify(data)  # JSON 데이터 반환

    except json.JSONDecodeError as jde:
        # JSON 파싱 중 오류
        return jsonify({"error": "JSON 파일을 파싱하는 중 오류 발생", "details": str(jde)}), 500

    except Exception as e:
        # 일반 오류 처리
        return jsonify({"error": "JSON 파일을 제공하는 중 오류 발생", "details": str(e)}), 500

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True)