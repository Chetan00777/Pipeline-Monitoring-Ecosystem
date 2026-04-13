import json
import boto3
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from botocore.exceptions import ClientError, EndpointConnectionError
from .models import SensorBuffer

logger = logging.getLogger(__name__)

# Initialize AWS SQS Client (Will fail gracefully if keys aren't set)
try:
        sqs_client = boto3.client(
        'sqs',
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN
    )
except Exception as e:
    logger.warning(f"AWS SQS initialization failed: {e}. Will operate in offline/buffer mode.")
    sqs_client = None

def get_queue_url(queue_name):
    """Retrieve SQS queue URL by name. Caches in memory for speed."""
    if not sqs_client:
        return None
    try:
        response = sqs_client.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']
    except ClientError as e:
        logger.error(f"Failed to get queue URL for {queue_name}: {e}")
        return None

def push_to_cloud(payload):
    """Attempt to push data to AWS SQS."""
    if not sqs_client:
        raise EndpointConnectionError(endpoint_url="offline")
    
    queue_url = get_queue_url(settings.SQS_PIPELINE_QUEUE)
    if not queue_url:
        raise EndpointConnectionError(endpoint_url="queue_not_found")

    # If it's a critical alert, you might optionally push to a secondary alert queue
    # Here we just push all data to the main queue
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(payload),
        MessageAttributes={
            'SensorType': {
                'DataType': 'String',
                'StringValue': payload.get('sensor_type', 'UNKNOWN')
            }
        }
    )

@csrf_exempt
def ingest_sensor_data(request):
    """
    Fog Node API Endpoint:
    Receives HTTP POST requests from pipeline sensors.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body)
        
        # --- FOG NODE EDGE PROCESSING ---
        # 1. We could add autonomous actions here
        # E.g., if H2S is CRITICAL, immediately close valves logically
        meta = payload.get('metadata', {})
        status = meta.get('status', 'NORMAL')
        hazard = meta.get('hazard_level', 'SAFE')

        if hazard == 'CRITICAL' or status == 'CRITICAL':
            logger.error(f"🚨🚨 FOG AUTONOMOUS ACTION: CRITICAL {payload['sensor_type']} detected on {payload['pipeline_segment']}. Triggering local shutdown protocols! 🚨🚨")
            # In a real system, you'd send an API call to the Valve Controller here

        # --- CLOUD DISPATCH or OFFLINE BUFFER ---
        try:
            # Try to push to AWS SQS
            push_to_cloud(payload)
            return JsonResponse({'status': 'Data received and queued to cloud'}, status=200)
            
        except (EndpointConnectionError, Exception) as e:
            # Connectivity down or AWS config missing -> Fallback to Local Fog Buffer
            logger.warning(f"Cloud unreachable ({e}). Saving to Fog Node Local Buffer.")
            SensorBuffer.objects.create(
                sensor_id=payload.get('sensor_id'),
                sensor_type=payload.get('sensor_type'),
                pipeline_segment=payload.get('pipeline_segment'),
                payload=payload
            )
            return JsonResponse({'status': 'Cloud down. Data buffered locally.'}, status=202)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Ingest Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
