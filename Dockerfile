# Python 기반 이미지에서 시작
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# git 및 git-lfs 설치
RUN apt-get update && apt-get install -y git git-lfs \
    && git lfs install \
    && rm -rf /var/lib/apt/lists/*

# Git 리포지토리 클론
RUN git clone https://github.com/BonjourBuerreBuerreCruasaint/spotrank-be.git /app

# 작업 디렉토리 변경
WORKDIR /app

# .env 파일을 컨테이너로 복사
COPY .env /app/.env

# 로컬의 큰 데이터 파일들을 한 번에 복사 (여러 파일 포함)
COPY C:/Users/USER/PycharmProjects/BBC/spotrank-be/data/* /app/data/

# filtered_output 파일을 Docker 이미지에 추가
COPY C:/Users/USER/PycharmProjects/BBC/spotrank-be/filtered_output /app/data/filtered_output.csv

COPY C:/Users/USER/PycharmProjects/BBC/spotrank-be/combined_order.csv /app/data/combined_order.csv

# JinFinalPeople.csv 파일을 Docker 이미지에 추가
COPY C:/Users/USER/PycharmProjects/BBC/spotrank-be/JinFinalPeople.csv /app/data/JinFinalPeople.csv

COPY C:/Users/USER/PycharmProjects/BBC/spotrank-be/modified_file.json /app/data/modified_file.json


# 필요한 파일들을 복사
COPY . ./ 

# .env 파일을 환경 변수로 로드 (python-dotenv 사용)
RUN pip install python-dotenv

# Flask 애플리케이션이 실행될 포트 노출
EXPOSE 5000

# Flask 실행 명령어 (dotenv로 환경 변수 로드)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
