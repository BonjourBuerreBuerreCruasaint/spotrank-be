import pandas as pd

# CSV 파일 읽기
input_file = 'store_info.csv/store_info.csv'  # 입력 파일 경로
output_file = 'filtered_output1.csv'  # 출력 파일 경로

# CSV 파일을 pandas DataFrame으로 읽어들임
df = pd.read_csv(input_file)

# '상권업종대분류명' 컬럼에서 '식당', '카페', '한식', '음식', '커피'를 포함하는 행만 필터링
filtered_df = df[df['상권업종대분류명'].str.contains('식당|카페|한식|음식|커피', na=False)]

# '도로명주소' 컬럼에서 특정 도로명(신촌, 대흥로 등)을 포함하는 행만 필터링
filtered_df = filtered_df[filtered_df['시군구명'].str.contains('서대문구|마포구', na=False)]

# 필요한 컬럼만 선택 (상호명, 시도명, 시군구명, 행정동명, 법정동명, 도로명주소, 경도, 위도)
columns_to_keep = ['상호명', '상권업종대분류명','상권업종중분류명','상권업종소분류명','시도명', '시군구명', '행정동명', '법정동명', '도로명주소', '경도', '위도']
filtered_df = filtered_df[columns_to_keep]

# 새로운 CSV 파일로 저장
filtered_df.to_csv(output_file, index=False)

print(f"필터링된 데이터가 {output_file}로 저장되었습니다.")
