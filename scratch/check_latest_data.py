import boto3
import os
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key

load_dotenv()

db = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_REGION_NAME', 'us-east-1')
)

try:
    table = db.Table(os.getenv('DYNAMODB_TABLE_NAME', 'PipelineData'))
    # Query for one type to check the latest timestamp
    response = table.query(
        IndexName='SensorTypeIndex',
        KeyConditionExpression=Key('sensor_type').eq('PRESSURE'),
        ScanIndexForward=False,
        Limit=5
    )
    items = response.get('Items', [])
    if items:
        for item in items:
            print(f"Sensor: {item.get('sensor_id')}, Time: {item.get('timestamp')}, Value: {item.get('value')}")
    else:
        print("No items found in DynamoDB.")
except Exception as e:
    print(f"Error: {e}")
