#해당 py는 aws lambda설정을 위해 만듦
from Poodding import

def lambda_handler(event, context):
    # 함수 로직 구현
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
