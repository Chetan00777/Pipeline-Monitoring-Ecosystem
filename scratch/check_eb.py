import boto3
import os
from dotenv import load_dotenv

load_dotenv()

eb = boto3.client(
    'elasticbeanstalk',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_REGION_NAME', 'us-east-1')
)

try:
    envs = eb.describe_environments()
    for env in envs['Environments']:
        print(f"App: {env['ApplicationName']}, Env: {env['EnvironmentName']}, Status: {env['Status']}, Health: {env['Health']}, URL: {env['CNAME']}")
except Exception as e:
    print(f"Error: {e}")
