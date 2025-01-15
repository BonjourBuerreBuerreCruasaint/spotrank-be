from flask import Flask, jsonify, request, session, Blueprint
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Welcome1!'  # Flask 시크릿 키 설정
logout_blueprint = Blueprint('logout', __name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# API 엔드포인트: 로그아웃
@logout_blueprint.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()  # 세션 데이터 전체 삭제
        response = jsonify({"message": "로그아웃 성공"})
        response.set_cookie('session', '', expires=0)
        return response
    except Exception as e:
        print(f"Error clearing session: {e}")
        return jsonify({"error": "세션 초기화 중 오류 발생"}), 500
if __name__ == '__main__':
    app.run(debug=True)