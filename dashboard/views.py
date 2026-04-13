import boto3
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from botocore.exceptions import ClientError
from fog_node.models import SensorBuffer
from concurrent.futures import ThreadPoolExecutor, as_completed
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)

# Cache for AWS Resource to avoid slow re-initialization
_DYNAMODB_RESOURCE = None

def get_dynamodb_resource():
    global _DYNAMODB_RESOURCE
    if _DYNAMODB_RESOURCE is None and settings.AWS_ACCESS_KEY_ID:
        try:
            session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_session_token=settings.AWS_SESSION_TOKEN,
                region_name=settings.AWS_REGION_NAME
            )
            # Add short timeouts to prevent hanging
            from botocore.config import Config
            config = Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 1})
            _DYNAMODB_RESOURCE = session.resource('dynamodb', config=config)
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB resource: {e}")
    return _DYNAMODB_RESOURCE

def query_sensor_data(table, s_type):
    try:
        response = table.query(
            IndexName='SensorTypeIndex',
            KeyConditionExpression=Key('sensor_type').eq(s_type),
            ScanIndexForward=False, # Latest first
            Limit=20
        )
        return s_type, response.get('Items', [])
    except Exception as e:
        logger.warning(f"Query failed for {s_type}: {e}")
        return s_type, []

def dashboard_home(request):
    """Render the main HTML dashboard."""
    return render(request, 'dashboard.html')

def api_system_status(request):
    """
    Optimized API for Dashboard.
    Uses ThreadPoolExecutor for parallel AWS queries.
    """
    data = {
        'PRESSURE': [], 'H2S_GAS': [], 'FLOW_RATE': [],
        'CORROSION': [], 'VALVE_POS': [], 'ALERT': []
    }
    
    readings = []
    source = "LOCAL_FOG"
    
    # --- 1. TRY DYNAMODB (CLOUD) ---
    db = get_dynamodb_resource()
    if db:
        try:
            table = db.Table(settings.DYNAMODB_TABLE_NAME)
            sensor_types = ['PRESSURE', 'H2S_GAS', 'FLOW_RATE', 'CORROSION', 'VALVE_POS', 'ALERT']
            
            # Parallel execution of 6 queries
            cloud_readings = []
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {executor.submit(query_sensor_data, table, st): st for st in sensor_types}
                for future in as_completed(futures):
                    s_type, items = future.result()
                    for item in items:
                        cloud_readings.append({
                            'payload': item,
                            'created_at': item.get('timestamp')
                        })
            
            if cloud_readings:
                source = "AWS_DYNAMODB"
                readings = cloud_readings
        except Exception as e:
            logger.warning(f"Cloud fetch error: {e}")

    # --- 2. FALLBACK TO LOCAL ---
    if not readings:
        recent_readings = SensorBuffer.objects.all().order_by('-created_at')[:50]
        for r in recent_readings:
            readings.append({
                'payload': r.payload,
                'created_at': r.created_at.isoformat()
            })

    # --- 3. PROCESS ---
    for reading in readings:
        payload = reading['payload']
        sensor_type = payload.get('sensor_type')
        
        entry = {
            'time': reading['created_at'],
            'value': payload.get('value'),
            'segment': payload.get('pipeline_segment')
        }
        
        if sensor_type in data and sensor_type != 'ALERT':
            data[sensor_type].append(entry)
            
        if sensor_type == 'ALERT':
            data['ALERT'].append({
                'time': entry['time'],
                'sensor': payload.get('sensor_id', 'SYSTEM'),
                'segment': entry['segment'],
                'message': payload.get('message', "System alert detected")
            })
        else:
            meta = payload.get('metadata', {})
            hazard = meta.get('hazard_level', 'SAFE')
            status = meta.get('status', 'NORMAL')
            
            if hazard == 'CRITICAL' or status == 'CRITICAL' or status == 'CLOSED':
                data['ALERT'].append({
                    'time': entry['time'],
                    'sensor': sensor_type,
                    'segment': entry['segment'],
                    'message': f"CRITICAL status detected on {sensor_type} ({payload.get('value')} {payload.get('unit')})"
                })

    # Final sort/limit
    for key in data:
        if key != 'ALERT':
            data[key] = sorted(data[key], key=lambda x: x['time'])[-20:]
        
    return JsonResponse({'source': source, 'data': data})
