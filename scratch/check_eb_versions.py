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
    versions = eb.describe_application_versions(ApplicationName='pipeline-monitor')
    for v in sorted(versions['ApplicationVersions'], key=lambda x: x['DateCreated'], reverse=True)[:5]:
        print(f"Version: {v['VersionLabel']}, Created: {v['DateCreated']}, Description: {v.get('Description', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
