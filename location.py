from flask import Flask, jsonify
import csv
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CSV 파일의 절대 경로 설정
file_path = r"C:\Users\rim\OneDrive - KNOU\바탕 화면\spotrank-be\filtered_output.csv"

def read_csv(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File does not exist at: {file_path}")
        return []

    locations = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            logger.info(f"CSV columns found: {reader.fieldnames}")

            for idx, row in enumerate(reader, 1):
                try:
                    name = row.get('상호명')
                    lat = row.get('위도')
                    lon = row.get('경도')

                    if any(v is None or v.strip() == '' for v in [name, lat, lon]):
                        logger.warning(f"Missing data in row {idx}: name={name}, lat={lat}, lon={lon}")
                        continue

                    latitude = float(lat)
                    longitude = float(lon)

                    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                        logger.warning(f"Coordinates out of range: lat={latitude}, lon={longitude}")
                        continue

                    locations.append({
                        "id": idx,
                        "name": name.strip(),
                        "latitude": latitude,
                        "longitude": longitude
                    })
                except Exception as e:
                    logger.error(f"Error processing row {idx}: {str(e)}")
                    continue

    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")

    return locations


@app.route('/locations', methods=['GET'])
def get_locations():
    try:
        locations = read_csv(file_path)
        if not locations:
            logger.warning("No locations data available")
            return jsonify({
                "success": False,
                "error": "No data available",
                "file_path": file_path,
                "debug_info": {
                    "file_exists": os.path.exists(file_path),
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
            }), 404

        return jsonify({
            "success": True,
            "data": locations,
            "count": len(locations)
        })
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"File path: {file_path}")
    logger.info(f"File exists: {os.path.exists(file_path)}")

    app.run(debug=True)
