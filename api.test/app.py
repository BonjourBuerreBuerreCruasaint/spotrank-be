import requests
import json

# API URL 및 인증 키
apiUrl = "https://api.odcloud.kr/api/nts-businessman/v1/validate"
service_key = "JC%2BrrD6VXQ7JVCU2mY6%2FV1CLXRhRnNKf4lTeRyE3NUcgGIax6OzwoCMW4VFbjEsVCFCsxyFk7lGuMzMHEPPmpg%3D%3D"

# 요청 헤더 및 데이터
headers = {
    'Content-Type': 'application/json'  # JSON 형식의 요청임을 명시
}

# ... existing code ...

data = {
    "businesses": [
        {
            "b_no": "0000000000",    # 사업자등록번호 (문자열, 10자리)
            "start_dt": "20250101",   # 개업일자 (문자열, YYYYMMDD)
            "p_nm": "홍길동"          # 대표자성명 (문자열)
        }
    ]
}

# ... existing code ...
# POST 요청 보내기
response = requests.post(f"{apiUrl}?serviceKey={service_key}", headers=headers, json=data)

# 응답 출력
print(response.status_code)  # HTTP 상태 코드 출력
print(response.json())       # JSON 응답 출력
