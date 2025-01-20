from flask import Flask, jsonify, Blueprint
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

colored_blueprint = Blueprint('colored_zone', __name__)

@colored_blueprint.route('/colored-zones', methods=['GET'])
def get_colored_zones():
    try:
        print("Loading CSV files...")
        filtered_df = pd.read_csv('filtered_output1.csv')
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

app.register_blueprint(colored_blueprint)

if __name__ == '__main__':
    app.run(debug=True)