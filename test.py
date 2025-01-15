from flask import Flask, render_template

# Flask 앱 생성
app = Flask(__name__)

# 라우팅 설정
@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/about")
def about():
    return render_template("about.html")  # HTML 파일 렌더링

if __name__ == "__main__":
    app.run(debug=True)  # 디버그 모드로 실행
