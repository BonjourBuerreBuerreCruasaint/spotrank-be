import requests
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

verify_business_blueprint = Blueprint('verify_business', __name__)
# 공공 API 키 설정
PUBLIC_API_URL = "https://api.odcloud.kr/api/nts-businessman/v1/status"
SERVICE_KEY = "wuT+UJm4T2EBtTIM7yrKqUNXQsMIMaq9P6/ibdg/b/SV9Wq1t2fDG/N1Cy+JCkUnbMLLPdPnBg184/npVGLp5A=="  # 발급받은 API 키 입력


@verify_business_blueprint.route('/verify-business', methods=['POST'])
def verify_business():
    data = request.get_json()
    print(f"Received data: {data}")
    business_number = data.get('businessNumber')
    opening_date = data.get('openingDate')
    opening_date = opening_date.replace('-', '')
    business_name = data.get('businessName')

    # 공공 API 요청 데이터
    payload = {
        "b_no": [business_number],  # 사업자등록번호
        "start_dt": opening_date,  # 개업일
        "p_nm": business_name,  # 대표자 성명
        "p_nm2": "",
        "b_nm": "",
        "corp_no": "",
        "b_sector": "",
        "b_type": "",
        "b_adr": ""
    }

    params = {
        "serviceKey": SERVICE_KEY
    }
    if not business_number or not opening_date or not business_name:
        return jsonify({"message": "모든 필드를 입력해주세요."}), 400

    try:
        # API 요청
        response = requests.post(PUBLIC_API_URL, json=payload, params=params)
        response_data = response.json()

        # API 응답 처리
        if response.status_code == 200:
            # 사업자 진위 여부 확인 결과
            status = response_data.get("data")[0].get("b_stt")
            message = response_data.get("data")[0].get("tax_type")
            return jsonify({"status": status, "message": message}), 200
        else:
            return jsonify({"error": response_data.get("message", "API 호출 실패")}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.register_blueprint(verify_business_blueprint)

if __name__ == '__main__':
    app.run(debug=True)