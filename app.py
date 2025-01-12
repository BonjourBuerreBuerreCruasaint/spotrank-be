import secrets

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from get_seouldata import get_seouldata_blueprint
from jinfinalpeople import jinfinalpeople_blueprint
from ranking import api_blueprint  # api.py에서 Blueprint 가져오기
from signup_business import business_join_blueprint
from colored_zone import colored_blueprint
from find_id import find_id_blueprint
from signup_user import signup_blueprint  # join.py에서 Blueprint 가져오기
from login import login_blueprint
from __make_sell_data__ import make_sell_data_blueprint  # make_sell_data.py에서 Blueprint 가져오기
from reset_password import reset_password_blueprint
from store_update import store_update_blueprint
from verify_business import verify_business_blueprint

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)  # 세션 암호화 키 설정
# CORS 설정
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

bcrypt = Bcrypt(app)
# Blueprint 등록 (각각에 url_prefix 추가)
app.register_blueprint(api_blueprint, url_prefix='/')
app.register_blueprint(make_sell_data_blueprint, url_prefix='/make-sell-data')
#app.register_blueprint(location_blueprint, url_prefix='/')
app.register_blueprint(signup_blueprint, url_prefix='/api')  # '/api/signup'을 올바르게 설정
app.register_blueprint(business_join_blueprint, url_prefix='/api')
app.register_blueprint(verify_business_blueprint, url_prefix='/api')
app.register_blueprint(find_id_blueprint, url_prefix='/api')
app.register_blueprint(reset_password_blueprint, url_prefix='/api')
app.register_blueprint(login_blueprint, url_prefix='/api')
app.register_blueprint(colored_blueprint, url_prefix='/api')
app.register_blueprint(store_update_blueprint, url_prefix='/api')
app.register_blueprint(jinfinalpeople_blueprint, url_prefix='/api')
app.register_blueprint(get_seouldata_blueprint,url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)  # 포트 지정 가능
