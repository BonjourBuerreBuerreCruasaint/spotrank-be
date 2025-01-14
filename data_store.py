import requests

# API 엔드포인트 URL
url = "api.odcloud.kr/api"

# GET 요청 보내기
response = requests.get(url)

# 응답 상태 코드 확인
if response.status_code == 200:
    # JSON 데이터를 파싱
    data = response.json()
    print("API 데이터:", data)
else:
    print(f"요청 실패: {response.status_code}")

    