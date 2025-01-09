import pandas as pd
import os
from datetime import datetime
import math  # NaN 체크를 위한 모듈

# 파일 경로 설정
output_dir = "./output"
combined_file_path = "combined_order.csv"


# 날짜 형식 확인 함수
def is_date(string):
    try:
        datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return True
    except (ValueError, TypeError):
        return False


# NaN 값 확인 함수
def is_nan(value):
    return value is None or (isinstance(value, float) and math.isnan(value))


# 폴더 내 orders.csv 파일 처리
all_files = [f for f in os.listdir(output_dir) if f.endswith("_orders.csv")]
combined_data = []

for file_name in all_files:
    file_path = os.path.join(output_dir, file_name)
    data = pd.read_csv(file_path)

    # 가게 이름 추출 (파일 이름에서 "_orders.csv" 제거)
    store_name = file_name.replace("_orders.csv", "")

    # 새로운 데이터 저장할 리스트
    processed_rows = []

    # 데이터 검사 및 분류
    for _, row in data.iterrows():
        processed_row = {
            "store_name": store_name,  # 가게 이름 추가
            "menu": None,
            "price": None,
            "order_time": None,
            "count": None,
        }
        for value in row.values:
            if isinstance(value, str):
                if is_date(value):
                    processed_row["order_time"] = value  # 날짜 형식
                elif processed_row["menu"] is None:
                    processed_row["menu"] = value  # 메뉴
            elif isinstance(value, (int, float)) and not is_nan(value):
                if value >= 100 and processed_row["price"] is None:
                    processed_row["price"] = int(value)  # 가격
                elif processed_row["count"] is None:
                    processed_row["count"] = int(value)  # 수량

        # 누락된 데이터에 기본값 추가
        if processed_row["count"] is None or is_nan(processed_row["count"]):
            processed_row["count"] = 1  # 기본 수량 값 설정
        if processed_row["price"] is None or is_nan(processed_row["price"]):
            processed_row["price"] = 0  # 기본 가격 값 설정 (필요 시 수정 가능)

        processed_rows.append(processed_row)

    # 처리된 데이터 추가
    combined_data.extend(processed_rows)

# 합친 데이터프레임 생성
combined_df = pd.DataFrame(combined_data)

# 결과 저장
combined_df.to_csv(combined_file_path, index=False, encoding="utf-8-sig")
print(f"Combined file saved at: {combined_file_path}")