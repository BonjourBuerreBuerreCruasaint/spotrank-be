from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
import os
import json
import pandas as pd
import csv

# Flask 애플리케이션 설정
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

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

# 새로운 라우트: /colored-zones
@app.route('/api/colored-zones', methods=['GET'])
def get_colored_zones():
    try:
        print("Loading CSV files...")
        filtered_df = pd.read_csv('filtered_output.csv')
        combined_df = pd.read_csv('combined_order.csv')
        print("CSV files loaded successfully.")

        # Merge DataFrames
        print("Merging DataFrames...")
        merged_df = pd.merge(filtered_df, combined_df, on='store_name')
        print("Merge completed.")

        # Generate hourly columns
        print("Generating hourly columns...")
        merged_df['hour'] = pd.to_datetime(merged_df['order_time']).dt.hour
        for hour in range(24):
            hour_col = f'{hour:02d}'  # '00', '01', ..., '23'
            merged_df[hour_col] = (merged_df['hour'] == hour).astype(int)
        print("Hourly columns generated.")

        # Group by store_name and aggregate
        print("Grouping and aggregating data...")
        hour_columns = [f'{hour:02d}' for hour in range(24)]
        merged_df['total_sales'] = merged_df[hour_columns].sum(axis=1)
        agg_dict = {col: 'sum' for col in hour_columns}  # Sum up hourly columns
        agg_dict.update({
            'latitude': 'first',
            'longitude': 'first',
            'total_sales': 'sum',
            'menu': lambda x: ', '.join(set(x)),  # Combine unique menus
            'order_time': 'count'  # Count total orders
        })

        grouped_df = merged_df.groupby('store_name').agg(agg_dict).reset_index()
        print("Data grouped and aggregated.")

        # Prepare final output without polygons and colors
        print("Preparing final output...")
        output = grouped_df[['store_name', 'latitude', 'longitude', 'total_sales', 'menu', 'order_time']].to_dict(orient='records')
        print("Output prepared successfully.")

        return jsonify(output)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)
