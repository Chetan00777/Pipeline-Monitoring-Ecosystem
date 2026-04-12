import boto3
import time
import random
import os
from datetime import datetime, timezone
from decimal import Decimal
from decouple import config

# Configuration
REGION = os.getenv('AWS_REGION_NAME', 'us-east-1')
TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'PipelineData')

# Credentials from environment
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')

if not AWS_ACCESS_KEY_ID or not AWS_SESSION_TOKEN:
    print("ERROR: AWS Credentials not found in environment!")
    exit(1)

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=REGION
)
table = session.resource('dynamodb').Table(TABLE_NAME)

def simulate():
    print("="*60)
    print("LIVE DATA SIMULATOR STARTED")
    print("Injecting fresh readings into Cloud DynamoDB to demonstrate live charts.")
    print("="*60)

    try:
        while True:
            # 1. Generate realistic jittery data
            pressure = 445 + random.uniform(-10, 10)
            flow = 1100 + random.uniform(-50, 50)
            h2s = 1.0 + random.uniform(-0.5, 0.5)
            corrosion = 9.2 + random.uniform(-0.01, 0.01)
            
            payloads = [
                {'sensor_id': 'live-p1', 'sensor_type': 'PRESSURE', 'value': pressure, 'unit': 'PSI'},
                {'sensor_id': 'live-f1', 'sensor_type': 'FLOW_RATE', 'value': flow, 'unit': 'L/min'},
                {'sensor_id': 'live-g1', 'sensor_type': 'H2S_GAS', 'value': h2s, 'unit': 'PPM'},
                {'sensor_id': 'live-c1', 'sensor_type': 'CORROSION', 'value': corrosion, 'unit': 'mm'},
                {'sensor_id': 'live-v1', 'sensor_type': 'VALVE_POS', 'value': 100, 'unit': '%'}
            ]

            ts = datetime.now(timezone.utc).isoformat()
            
            for p in payloads:
                p['timestamp'] = ts
                p['pipeline_segment'] = 'SEGMENT-LIVE'
                p['value'] = Decimal(str(round(p['value'], 3)))
                table.put_item(Item=p)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushed batch of 5 readings to Cloud.")
            
            # Periodic mock alerts (every 30 seconds approx)
            if int(time.time()) % 30 < 2:
                mock_alert = {
                    'sensor_id': 'alert-001',
                    'timestamp': ts,
                    'pipeline_segment': 'SEGMENT-LIVE',
                    'sensor_type': 'ALERT',
                    'message': "Routine Pipeline Segment Integrity Check - OK",
                    'severity': 'INFO'
                }
                table.put_item(Item=mock_alert)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushed Maintenance Alert.")

            time.sleep(2) # Matched frequency for smoother charts
            
    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == '__main__':
    simulate()
