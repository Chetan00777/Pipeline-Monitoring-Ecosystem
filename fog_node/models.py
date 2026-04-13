from django.db import models
from django.utils import timezone


class BufferedPayload(models.fields.Field):
    pass # Simple placeholder for custom field if needed

class SensorBuffer(models.Model):
    """
    Offline buffer for sensor data when cloud connectivity drops.
    Acts as the 'Fog' storage layer.
    """
    sensor_id = models.CharField(max_length=50)
    sensor_type = models.CharField(max_length=50)
    pipeline_segment = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    synced = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sensor_type} ({self.pipeline_segment}) - Synced: {self.synced}"
