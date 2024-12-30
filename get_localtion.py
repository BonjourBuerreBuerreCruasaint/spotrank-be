from flask import Flask, request, jsonify, Blueprint
import requests

location_blueprint = Blueprint('get_location', __name__)


# IP 주소를 가져오는 함수
def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response['ip']  # IP 주소 문자열 반환


# 위치 정보를 반환하는 라우트
@location_blueprint.route('/get_location', methods=['GET'])
def get_location():
    try:
        # IP 주소 가져오기
        ip_address = get_ip()

        # ipapi.co API로 위치 정보 가져오기
        response = requests.get(f'https://whtop.com/tools.ip/{ip_address}').json()

        # 위치 데이터 정리
        latitude = response['location']['latitude']
        longitude = response['location']['longitude']

        # 결과 반환
        return jsonify({latitude,longitude})

    except Exception as e:
        # 에러 처리
        return jsonify({"error": str(e)}), 500


# Flask 애플리케이션 생성 및 블루프린트 등록
app = Flask(__name__)
app.register_blueprint(location_blueprint)

if __name__ == '__main__':
    app.run(debug=True)