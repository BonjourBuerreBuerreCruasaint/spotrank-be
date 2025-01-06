import boto3
from flask import Flask, request, jsonify, Blueprint
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)
send_email_blueprint = Blueprint('send_email', __name__)

# AWS SES 클라이언트 설정
ses_client = boto3.client('ses', region_name='ap-northeast-2')  # SES 서비스가 있는 AWS 리전 설정

@send_email_blueprint.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    recipient_email = data.get('email')
    subject = data.get('subject')
    body_text = data.get('body_text')

    if not recipient_email or not subject or not body_text:
        return jsonify({'error': '이메일, 제목, 본문을 모두 입력해야 합니다.'}), 400

    try:
        # 이메일 메시지 작성
        response = ses_client.send_email(
            Source='your-verified-email@example.com',  # SES에서 확인된 이메일
            Destination={
                'ToAddresses': [recipient_email],
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                    },
                },
            }
        )
        return jsonify({'message': '이메일이 발송되었습니다.'}), 200

    except (NoCredentialsError, PartialCredentialsError):
        return jsonify({'error': 'AWS 자격 증명이 누락되었습니다.'}), 500
    except Exception as e:
        return jsonify({'error': f'이메일 발송에 실패했습니다: {str(e)}'}), 500

app.register_blueprint(send_email_blueprint)

if __name__ == '__main__':
    app.run(debug=True)