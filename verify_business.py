import requests
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS

app = Flask(__name__)
app.secret_key='Welcome1!'
CORS(app, resources={r"/api/*": {"origins": "http://spotrank.store"}})

verify_business_blueprint = Blueprint('verify_business', __name__)
# 공공 API 키 설정
PUBLIC_API_URL = "https://api.odcloud.kr/api/nts-businessman/v1/validate"
SERVICE_KEY = "L3YjCW2L1CeEnfaIBq0Z79BrI6EcRtps/Zh13BYUIyGnZFlkUwEC/sLS9ys6QlcxipTW9CPILDZDS8ZN+woowg=="  # 발급받은 API 키 입력


@verify_business_blueprint.route('/verify-business', methods=['POST'])
def verify_business():
    data = request.get_json()
    print(f"Received data: {data}")
    business_number = data.get('businessNumber')
    opening_date = data.get('openingDate')
    opening_date = opening_date.replace('-', '')
    business_name = data.get('businessName')
    print(opening_date)
    print(PUBLIC_API_URL)
    # 공공 API 요청 데이터
    payload = {
        "businesses": [  # 요청 형식에 맞게 수정
            {
                "b_no": business_number,  # 사업자등록번호
                "start_dt": opening_date,  # 개업일
                "p_nm": business_name,  # 대표자 성명
                "p_nm2": "",
                "b_nm": "",
                "corp_no": "",
                "b_sector": "",
                "b_type": "",
                "b_adr": ""
            }
        ]
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
        print(response_data)
        # API 응답 처리
        if response.status_code == 200:
            api_data = response_data.get("data", [{}])[0]

            # 1. 데이터 필드 존재 여부 확인
            if not api_data:
                return jsonify({"message": "API 응답에 유효한 데이터가 없습니다."}), 400

            # 2. 상태 코드 확인
            status = api_data.get("b_stt")  # 사업자 상태 코드
            tax_type = api_data.get("tax_type")  # 과세 유형
            valid_check = api_data.get("valid")

            # 3. 조건 검사 (사업 상태 및 기타 매칭)
            if valid_check == '02':
                return jsonify({
                    "message": "사업자등록번호, 이름, 개업일이 일치하지 않습니다.",
                    "status": status
                }), 400

            return jsonify({
                "message": "사업자 확인 완료",
                "status": status
            }), 200
        else:
            return jsonify({"error": response_data.get("message", "API 호출 실패")}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.register_blueprint(verify_business_blueprint)

if __name__ == '__main__':
    app.run(debug=True)