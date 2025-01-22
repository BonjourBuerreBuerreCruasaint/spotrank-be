# Python 기반 이미지에서 시작
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# git 및 git-lfs 설치
RUN apt-get update && apt-get install -y git git-lfs \
    && git lfs install \
    && rm -rf /var/lib/apt/lists/*

# 필요한 파일들을 복사
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# .env 파일을 컨테이너로 복사
COPY .env /app/.env

# 애플리케이션 코드 복사
COPY . ./

# git-lfs로 LFS 파일 복구
RUN git lfs pull

# .env 파일을 환경 변수로 로드 (python-dotenv 사용)
RUN pip install python-dotenv

# Flask 애플리케이션이 실행될 포트 노출
EXPOSE 5000

# Flask 실행 명령어 (dotenv로 환경 변수 로드)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
