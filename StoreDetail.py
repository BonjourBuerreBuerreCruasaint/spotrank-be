from flask import Flask, jsonify, request

app = Flask(__name__)

# 더미 데이터
store_data = {
    "id": 1,
    "name": "커피빈 신촌점",
    "category": "카페",
    "address": "서울 서대문구 연세로 8-1 VERTIGO",
    "phone": "0000-0000-0000",
    "opening_hours": "월-일 00:00-24:00",
    "description": "가게 소개글이 들어갈 자리입니다.",
    "rankings": [
        {"rank": 1, "menu": "아메리카노"},
        {"rank": 2, "menu": "카페라떼"},
        {"rank": 3, "menu": "바닐라 라떼"},
        {"rank": 4, "menu": "카라멜 마키아토"},
        {"rank": 5, "menu": "초코 프라페"},
    ],
    "images": {
        "main": "https://via.placeholder.com/500x500",
        "sub": [f"https://via.placeholder.com/500x500?image={i}" for i in range(6)],
    },
    "location": {"lat": 37.556229, "lng": 126.937079},  # 위도, 경도
}

@app.route('/api/store-detail', methods=['GET'])
def get_store_detail():
    """매장 상세 정보 반환"""
    store_id = request.args.get("storeId")  # 필요한 경우 storeId 사용
    return jsonify(store_data)

@app.route('/api/store-rankings', methods=['GET'])
def get_store_rankings():
    """매장 인기 메뉴 랭킹 반환"""
    return jsonify({"rankings": store_data["rankings"]})

@app.route('/api/store-images', methods=['GET'])
def get_store_images():
    """매장 이미지 반환"""
    return jsonify(store_data["images"])

@app.route('/api/store-map-location', methods=['GET'])
def get_store_map_location():
    """매장 지도 위치 반환"""
    return jsonify(store_data["location"])

if __name__ == '__main__':
    app.run(debug=True)