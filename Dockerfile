# Python 기반 이미지에서 시작
FROM python:3.9-slim

# UTF-8 인코딩 설정
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일들을 복사
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# .env 파일을 컨테이너로 복사
COPY .env /app/.env

# 애플리케이션 코드 복사
COPY . ./

# .env 파일을 환경 변수로 로드 (python-dotenv 사용)
RUN pip install python-dotenv

# Flask 애플리케이션이 실행될 포트 노출
EXPOSE 5000

# Flask 실행 명령어 (dotenv로 환경 변수 로드)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
