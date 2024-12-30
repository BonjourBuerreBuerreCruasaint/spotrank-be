from flask import Flask
from flask_cors import CORS
from api import api_blueprint  # api.py에서 Blueprint 가져오기
from get_localtion import location_blueprint
from make_sell_data import make_sell_data_blueprint
app = Flask(__name__)
CORS(app)
# Blueprint 등록
app.register_blueprint(api_blueprint)
app.register_blueprint(make_sell_data_blueprint)
app.register_blueprint(location_blueprint)

if __name__ == '__main__':
    app.run(debug=True)