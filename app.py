from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from api import api_blueprint  # api.py에서 Blueprint 가져오기
#from get_location import location_blueprint  # get_location.py에서 Blueprint 가져오기
from join import join_blueprint  # join.py에서 Blueprint 가져오기
from make_sell_data import make_sell_data_blueprint  # make_sell_data.py에서 Blueprint 가져오기

app = Flask(__name__)

# CORS 설정
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
bcrypt = Bcrypt(app)
# Blueprint 등록 (각각에 url_prefix 추가)
app.register_blueprint(api_blueprint, url_prefix='/')
app.register_blueprint(make_sell_data_blueprint, url_prefix='/make-sell-data')
#app.register_blueprint(location_blueprint, url_prefix='/')
app.register_blueprint(join_blueprint, url_prefix='/signup')  # '/api/signup'을 올바르게 설정

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 포트 지정 가능