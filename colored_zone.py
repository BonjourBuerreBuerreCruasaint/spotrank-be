from flask import Flask, jsonify, Blueprint
import pandas as pd
from flask_cors import CORS
import os
import boto3
from io import StringIO

app = Flask(__name__)

# CORS 설정: 배포된 프론트엔드의 외부 IP나 도메인으로 변경
CORS(app, resources={r"/api/*": {"origins": "http://acde99d041b9e4508a570a83ad12fd84-1969489418.ap-northeast-2.elb.amazonaws.com "}}, supports_credentials=True)

colored_blueprint = Blueprint('colored_zone', __name__)

# S3에서 파일을 읽는 함수
def read_csv_from_s3(bucket_name, file_key):
    s3_client = boto3.client('s3')
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = obj['Body'].read().decode('utf-8')
        return pd.read_csv(StringIO(file_content))  # CSV를 pandas DataFrame으로 읽기
    except Exception as e:
        print(f"Error reading {file_key} from S3: {e}")
        return None

@colored_blueprint.route('/colored-zones', methods=['GET'])
def get_colored_zones():
    try:
        print("Loading CSV files from S3...")

        # S3에서 파일 읽기
        filtered_df = read_csv_from_s3('backendsource', 'filtered_output.csv')
        combined_df = read_csv_from_s3('backendsource', 'combined_order.csv')

        # 파일이 제대로 로드되지 않으면 오류 반환
        if filtered_df is None or combined_df is None:
            return jsonify({"error": "Failed to load CSV files from S3"}), 500

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
        # 필요한 열만 선택하고, JSON으로 변환
        output = grouped_df[['store_name', 'latitude', 'longitude', 'total_sales', 'menu', 'order_time']].to_dict(orient='records')
        print("Output prepared successfully.")

        return jsonify(output)  # JSON 형식으로 반환

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

app.register_blueprint(colored_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
