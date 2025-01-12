from flask import Flask, jsonify, Blueprint
import os

from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

jinfinalpeople_blueprint = Blueprint('jinfinalpeople', __name__)

@jinfinalpeople_blueprint.route('/jinfinalpeople', methods=['GET'])
def serve_jinfinalpeople():
    try:
        # 현재 파일의 디렉토리 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'JinFinalPeople.csv')

        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            return jsonify({"error": "파일이 존재하지 않습니다."}), 404

        # CSV 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.readlines()  # 파일 내용을 줄 단위로 읽음

        return jsonify({"content": data})  # CSV 데이터 반환

    except Exception as e:
        # 오류 처리
        return jsonify({"error": "CSV 파일을 제공하는 중 오류 발생", "details": str(e)}), 500

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True)