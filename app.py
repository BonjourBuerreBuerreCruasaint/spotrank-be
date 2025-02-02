import secrets
from datetime import timedelta

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from get_menu_data import get_menu_data_blueprint
from get_seouldata import get_seouldata_blueprint
from jinfinalpeople import jinfinalpeople_blueprint
from logout import logout_blueprint
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

app.secret_key = 'Welcome1!' # 세션 암호화 키 설정

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # 세션 유지 시간 설정 (여기선 1일로 설정)
app.config['SESSION_COOKIE_SECURE'] = False  # 개발 환경에서는 False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 세션 쿠키 SameSite 설정
# CORS 설정
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}},supports_credentials=True)

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
app.register_blueprint(get_menu_data_blueprint, url_prefix='/api')
app.register_blueprint(logout_blueprint, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)  # 포트 지정 가능
