import pandas as pd
import random
from datetime import datetime, timedelta
import os

# CSV 파일 읽기
file_path = "filtered_output.csv"  # 파일 경로를 지정하세요.
data = pd.read_csv(file_path)

# 업종 소분류별 메뉴 목록 정의
menu_dict = {
    "일식 면 요리": ["라멘", "우동", "소바"],
    "카페": ["아메리카노", "카푸치노", "케이크"],
    "생맥주 전문": ["IPA", "필스너", "흑맥주"],
    "요리 주점": ["닭강정", "감자튀김", "떡볶이"],
    "일식 회/초밥": ["연어초밥", "참치회", "광어회"],
    "김밥/만두/분식": ["김밥", "떡볶이", "만두"],
    "빵/도넛": ["크루아상", "도넛", "머핀"],
    # 필요한 업종 소분류 추가
}

# 랜덤 가격 생성 함수
def random_price():
    return random.randint(1000, 30000)

# 랜덤 주문 시간 생성 함수
def random_order_time():
    now = datetime.now()
    random_minutes = random.randint(0, 1440)  # 하루(24시간) 내에서 랜덤 분
    return now - timedelta(minutes=random_minutes)

# 결과 저장 디렉토리 생성
output_dir = "./output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 기타 메뉴 제외하고 저장
for _, row in data.iterrows():
    try:
        # 상호명과 업종 소분류 추출
        store_name = row["상호명"].replace("/", "_")  # 파일 이름에 슬래시 제거
        sub_category = row["상권업종소분류명"]

        # 메뉴와 가격 생성
        menus = menu_dict.get(sub_category, ["기타 메뉴"])
        if "기타 메뉴" in menus:
            continue  # 기타 메뉴만 있는 업종은 건너뜀

        menu_data = [{"menu": menu, "price": random_price()} for menu in menus]

        # 주문 데이터 생성 (100개)
        order_data = []
        for _ in range(100):
            order = {
                "menu": random.choice(menus),
                "price": random_price(),
                "order_time": random_order_time().strftime("%Y-%m-%d %H:%M:%S"),
            }
            order_data.append(order)

        # 메뉴 테이블 CSV 저장
        menu_df = pd.DataFrame(menu_data)
        menu_file_path = os.path.join(output_dir, f"{store_name}_menu.csv")
        menu_df.to_csv(menu_file_path, index=False, encoding="utf-8-sig")

        # 주문 테이블 CSV 저장
        order_df = pd.DataFrame(order_data)
        order_file_path = os.path.join(output_dir, f"{store_name}_orders.csv")
        order_df.to_csv(order_file_path, index=False, encoding="utf-8-sig")

    except KeyError as e:
        print(f"누락된 키 오류 발생: {e}")
    except Exception as e:
        print(f"오류 발생: {e}")