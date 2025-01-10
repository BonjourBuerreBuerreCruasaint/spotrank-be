
import pandas as pd
import random
from datetime import datetime, timedelta
import os
import re

#파일이름 허용되지 않는 문자 제거
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


# CSV 파일 읽기
file_path = "filtered_output1.csv"  # 파일 경로를 지정하세요.
data = pd.read_csv(file_path)

# 업종 소분류별 메뉴 목록 정의
menu_dict = {
    "일식 면 요리": ["라멘", "우동", "소바", "탄탄멘"],
    "카페": ["아메리카노", "카푸치노", "케이크", "라떼", "핫초코"],
    "생맥주 전문": ["IPA", "필스너", "흑맥주", "라거", "에일"],
    "요리 주점": ["닭강정", "감자튀김", "떡볶이", "어묵탕", "모듬전"],
    "일식 회/초밥": ["연어초밥", "참치회", "광어회", "우니초밥", "장어덮밥"],
    "김밥/만두/분식": ["김밥", "떡볶이", "만두", "순대", "튀김"],
    "빵/도넛": ["크루아상", "도넛", "머핀", "치즈케이크", "타르트"],
    "한식": ["된장찌개", "김치찌개", "제육볶음", "비빔밥", "불고기"],
    "중식": ["짜장면", "짬뽕", "탕수육", "마라탕", "깐풍기"],
    "양식": ["스테이크", "파스타", "피자", "샐러드", "리조또"],
    "패스트푸드": ["햄버거", "치킨너겟", "프렌치프라이", "핫도그", "콜라"],
    "아이스크림/디저트": ["아이스크림", "와플", "빙수", "마카롱", "쿠키"],
    "피자 전문점": ["마르게리타", "고르곤졸라", "불고기피자", "포테이토피자", "콤비네이션"],
    "치킨 전문점": ["후라이드치킨", "양념치킨", "간장치킨", "마늘치킨", "허니콤보"],
    "족발/보쌈": ["족발", "보쌈", "쟁반국수", "막국수", "김치전"],
    "샌드위치/샐러드": ["치킨샐러드", "에그샌드위치", "BLT샌드위치", "클럽샌드위치", "과일샐러드"],
    "해산물": ["조개찜", "문어숙회", "낙지볶음", "해물파전", "바지락칼국수"],
    "베이커리": ["바게트", "스콘", "브리오슈", "파네토네", "체다치즈빵"],
    "뷔페": ["초밥", "스테이크", "탕수육", "피자", "샐러드"],
}

# 랜덤 가격 생성 함수 (정수형으로 반환)
def random_price():
    return int(random.randint(10, 500) * 100)  # 1,000원 ~ 50,000원

# 랜덤 수량 생성 함수
def random_count():
    return random.randint(1, 30)  # 1부터 30까지의 랜덤 수량

# 랜덤 주문 시간 생성 함수
def random_order_time():
    now = datetime.now()
    random_minutes = random.randint(0, 1440)  # 하루(24시간) 내에서 랜덤 분
    return now - timedelta(minutes=random_minutes)

# 랜덤 컬럼명 선택
menu_column_names = ["menu", "메뉴", "제품명", "메뉴명"]
price_column_names = ["price", "가격", "판매금액", "금액"]
time_column_names = ["order_time", "주문시간", "구매시각"]
count_column_names = ["count", "수량", "개수", "갯수"]

# 결과 저장 디렉토리 생성
output_dir = "C:./output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
    
# 기타 메뉴 제외하고 저장
for _, row in data.iterrows():
    try:
        # 상호명과 업종 소분류 추출
        store_name = row["store_name"].replace("/", "_")  # 파일 이름에 슬래시 제거
        sub_category = row["상권업종소분류명"]

        # 메뉴와 가격 데이터 생성
        menus = menu_dict.get(sub_category, ["기타 메뉴"])
        if "기타 메뉴" in menus:
            continue  # 기타 메뉴만 있는 업종은 건너뜀

        menu_data = [{"menu": menu, "price": random_price()} for menu in menus]

        # 주문 데이터 생성 (100개)
        order_data = []
        for _ in range(100):
            selected_menu = random.choice(menu_data)
            order = {
                random.choice(menu_column_names): selected_menu["menu"],
                random.choice(price_column_names): selected_menu["price"],
                random.choice(time_column_names): random_order_time().strftime("%Y-%m-%d %H:%M:%S"),
                random.choice(count_column_names): random_count(),
            }
            # 수량 컬럼이 항상 포함되도록 보장
            if not any(col in order for col in count_column_names):
                order[count_column_names[0]] = random_count()
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
