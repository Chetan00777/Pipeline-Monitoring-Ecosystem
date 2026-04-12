import boto3
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from botocore.exceptions import ClientError
from fog_node.models import SensorBuffer

logger = logging.getLogger(__name__)

def dashboard_home(request):
    """Render the main HTML dashboard."""
    return render(request, 'dashboard.html')

def api_system_status(request):
    """
    API for the Dashboard frontend.
    Priority:
    1. Try to fetch from AWS DynamoDB (Processed Cloud Data)
    2. Fallback to Local SQLite (Fog Node Buffer) if Cloud is unreachable
    """
    
    # Data structure for the frontend
    data = {
        'PRESSURE': [],
        'H2S_GAS': [],
        'FLOW_RATE': [],
        'CORROSION': [],
        'VALVE_POS': [],
        'ALERT': []
    }
    
    readings = []
    source = "LOCAL_FOG"

    # --- 1. TRY DYNAMODB (CLOUD) ---
    try:
        if settings.AWS_ACCESS_KEY_ID:
            session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_session_token=settings.AWS_SESSION_TOKEN,
                region_name=settings.AWS_REGION_NAME
            )
            db = session.resource('dynamodb')
            table = db.Table(settings.DYNAMODB_TABLE_NAME)
            
            # High-Performance Querying:
            # Instead of a slow Scan, we query the 'SensorTypeIndex' GSI 
            # for the latest 20 readings of each specific sensor type.
            from boto3.dynamodb.conditions import Key
            
            sensor_types = ['PRESSURE', 'H2S_GAS', 'FLOW_RATE', 'CORROSION', 'VALVE_POS', 'ALERT']
            cloud_readings = []
            
            for s_type in sensor_types:
                try:
                    response = table.query(
                        IndexName='SensorTypeIndex',
                        KeyConditionExpression=Key('sensor_type').eq(s_type),
                        ScanIndexForward=False, # Get latest items first
                        Limit=20
                    )
                    items = response.get('Items', [])
                    for item in items:
                        cloud_readings.append({
                            'payload': item,
                            'created_at': item.get('timestamp')
                        })
                except ClientError as e:
                    # If index is still creating, this might fail - fallback to local is handled below
                    logger.warning(f"GSI Query failed for {s_type}: {e}")

            if cloud_readings:
                source = "AWS_DYNAMODB"
                readings = cloud_readings
    except Exception as e:
        logger.warning(f"Failed to fetch from DynamoDB: {e}")

    # --- 2. FALLBACK TO LOCAL SQLITE (FOG) ---
    if not readings:
        recent_readings = SensorBuffer.objects.all().order_by('-created_at')[:50]
        for r in recent_readings:
            readings.append({
                'payload': r.payload,
                'created_at': r.created_at.isoformat()
            })

    # --- 3. PROCESS FOR DASHBOARD ---
    for reading in readings:
        payload = reading['payload']
        sensor_type = payload.get('sensor_type')
        meta = payload.get('metadata', {})
        
        entry = {
            'time': reading['created_at'],  # Full ISO timestamp for JS conversion
            'value': payload.get('value'),
            'segment': payload.get('pipeline_segment')
        }
        
        if sensor_type in data:
            data[sensor_type].append(entry)
            
        # Extract critical alerts (Legacy + Direct Alert records)
        if sensor_type == 'ALERT':
            data['ALERT'].append({
                'time': entry['time'],
                'sensor': 'SYSTEM',
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

    # Sort and reverse for charts
    for key in data:
        if key != 'ALERT':
            data[key] = sorted(data[key], key=lambda x: x['time'])[-20:]
        
    return JsonResponse({'source': source, 'data': data})
