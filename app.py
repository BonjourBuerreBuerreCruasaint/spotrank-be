from flask import Flask
from flask_cors import CORS
from api import api_blueprint  # api.py에서 Blueprint 가져오기

app = Flask(__name__)
CORS(app)

# Blueprint 등록
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)