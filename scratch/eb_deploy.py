import boto3
import os
import zipfile
import time
from dotenv import load_dotenv

load_dotenv()

APP_NAME = 'pipeline-monitor'
ENV_NAME = 'pipeline-monitor-live'
REGION = os.getenv('AWS_REGION_NAME', 'us-east-1')

eb = boto3.client(
    'elasticbeanstalk',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=REGION
)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=REGION
)

def create_zip():
    filename = f"deployment-{int(time.time())}.zip"
    print(f"Creating {filename}...")
    
    # Exclude List
    exclude = ['.git', '.venv', 'scratch', 'pipeline_data.db', '__pycache__', 'staticfiles']
    
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Prune excluded dirs
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                if file not in exclude and not file.endswith('.zip') and not file == '.env':
                    path = os.path.join(root, file)
                    zipf.write(path, os.path.relpath(path, '.'))
                    
    return filename

def deploy():
    # 1. Zip
    zip_file = create_zip()
    
    # 2. Find/Create S3 Storage
    storage = eb.create_storage_location()
    bucket = storage['S3Bucket']
    key = f"apps/{APP_NAME}/{zip_file}"
    
    # 3. Upload
    print(f"Uploading to s3://{bucket}/{key}...")
    s3.upload_file(zip_file, bucket, key)
    
    # 4. Create Version
    version_label = f"v-{int(time.time())}"
    print(f"Creating application version {version_label}...")
    eb.create_application_version(
        ApplicationName=APP_NAME,
        VersionLabel=version_label,
        SourceBundle={
            'S3Bucket': bucket,
            'S3Key': key
        },
        AutoCreateApplication=False,
        Description='Optimized Dashboard with Alert Fix'
    )
    
    # 5. Update Environment
    print(f"Updating environment {ENV_NAME} to version {version_label}...")
    eb.update_environment(
        EnvironmentName=ENV_NAME,
        VersionLabel=version_label
    )
    
    print("Deployment triggered! Waiting for environment to transition...")
    
    # cleanup local zip
    os.remove(zip_file)

if __name__ == "__main__":
    deploy()
