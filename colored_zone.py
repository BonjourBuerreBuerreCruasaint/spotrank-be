from flask import Flask, jsonify, Blueprint
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

colored_blueprint = Blueprint('colored_zone', __name__)

@colored_blueprint.route('/colored-zones', methods=['GET'])
def get_colored_zones():
    try:
        # Load CSV files
        filtered_df = pd.read_csv('filtered_output.csv')
        combined_df = pd.read_csv('combined_order.csv')

        # Merge DataFrames
        merged_df = pd.merge(filtered_df, combined_df, on='store_name')

        # Generate hourly columns
        merged_df['hour'] = pd.to_datetime(merged_df['order_time']).dt.hour
        for hour in range(24):
            hour_col = f'{hour:02d}'  # '00', '01', ..., '23'
            merged_df[hour_col] = (merged_df['hour'] == hour).astype(int)

        # Group by store_name and aggregate
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

        # Sort by total_sales
        grouped_df = grouped_df.sort_values(by='total_sales', ascending=False)

        # Assign color categories based on sales ranking
        total_count = len(grouped_df)
        thresholds = {
            "red": int(total_count * 0.10),
            "orange": int(total_count * 0.25),
            "yellow": int(total_count * 0.25),
            "green": int(total_count * 0.20),
            "blue": int(total_count * 0.20),
        }

        colors = ["red"] * thresholds["red"] + \
                 ["orange"] * thresholds["orange"] + \
                 ["yellow"] * thresholds["yellow"] + \
                 ["green"] * thresholds["green"] + \
                 ["blue"] * thresholds["blue"]

        grouped_df['color'] = colors

        # Calculate polygon for each store
        def calculate_polygon(latitude, longitude, range_km=0.00008):  # 범위 0.001도 (약 100m)
            return [
                [latitude - range_km, longitude - range_km],
                [latitude - range_km, longitude + range_km],
                [latitude + range_km, longitude + range_km],
                [latitude + range_km, longitude - range_km],
            ]

        grouped_df['polygon'] = grouped_df.apply(
            lambda row: calculate_polygon(row['latitude'], row['longitude']), axis=1
        )

        # Prepare final output
        output = grouped_df[['store_name', 'polygon', 'color', 'total_sales', 'menu', 'order_time']].to_dict(orient='records')

        return jsonify(output)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


app.register_blueprint(colored_blueprint)

if __name__ == '__main__':
    app.run(debug=True)