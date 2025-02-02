from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
import csv
import time

app = Flask(__name__)
CORS(app)  # CORS 허용

# 정적 파일을 제공하는 라우트
@app.route('/api/seouldata', methods=['GET'])
def serve_seouldata():
    try:
        # 현재 파일의 디렉토리 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'modified_file.json')

        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            return jsonify({"error": "파일이 존재하지 않습니다."}), 404

        # JSON 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # JSON 파일을 파싱

        # 데이터 검증 (latitude, longitude 값 확인)
        for entry in data:
            if entry.get("latitude") is None or entry.get("longitude") is None:
                print(f"위도 또는 경도가 유효하지 않음: 위도={entry.get('latitude')}, 경도={entry.get('longitude')}")

        return jsonify(data)  # JSON 데이터 반환

    except json.JSONDecodeError:
        return jsonify({"error": "JSON 파일을 파싱하는 중 오류 발생"}), 500
    except Exception as e:
        return jsonify({"error": "JSON 파일을 제공하는 중 오류 발생", "details": str(e)}), 500

# JinFinalPeople.csv를 제공하는 라우트
@app.route('/api/jinfinalpeople', methods=['GET'])
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
        return jsonify({"error": "CSV 파일을 제공하는 중 오류 발생", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
