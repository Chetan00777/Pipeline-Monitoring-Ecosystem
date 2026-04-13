"""
Base Sensor Class
=================
All sensor simulators inherit from this base class.
Each sensor runs in its own thread, generating realistic data
and dispatching payloads to the fog node at a configurable rate.
"""
import time
import uuid
import threading
import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseSensor(threading.Thread):
    """
    Abstract base class for all pipeline sensor simulators.

    Attributes:
        sensor_id       : Unique identifier for this sensor instance
        sensor_type     : Type label (e.g. 'PRESSURE', 'H2S_GAS')
        pipeline_segment: Which segment of the pipeline this sensor monitors
        dispatch_interval: How often (seconds) to send data to the fog node
        fog_node_url    : HTTP endpoint of the fog node
        running         : Thread control flag
    """

    def __init__(self, pipeline_segment: str, dispatch_interval: int = 3,
                 fog_node_url: str = 'http://127.0.0.1:8000/fog/ingest/'):
        super().__init__(daemon=True)
        self.sensor_id        = str(uuid.uuid4())[:8]
        self.sensor_type      = 'BASE'
        self.pipeline_segment = pipeline_segment
        self.dispatch_interval = dispatch_interval
        self.fog_node_url     = fog_node_url
        self.running          = True

    def generate_reading(self) -> dict:
        """
        Override in subclass.
        Must return a dict with at least: {'value': float, 'unit': str}
        """
        raise NotImplementedError("Subclasses must implement generate_reading()")

    def build_payload(self, reading: dict) -> dict:
        """Build the standard sensor payload sent to the fog node."""
        return {
            'sensor_id'       : self.sensor_id,
            'sensor_type'     : self.sensor_type,
            'pipeline_segment': self.pipeline_segment,
            'value'           : reading['value'],
            'unit'            : reading['unit'],
            'metadata'        : reading.get('metadata', {}),
            'timestamp'       : datetime.now(timezone.utc).isoformat(),
        }

    def dispatch_to_fog(self, payload: dict):
        """Send the sensor payload to the fog node via HTTP POST."""
        try:
            response = requests.post(
                self.fog_node_url,
                json=payload,
                timeout=5,
                headers={'Content-Type': 'application/json'},
            )
            if response.status_code == 200:
                logger.debug(f"[{self.sensor_type}] Segment {self.pipeline_segment} → Fog OK")
            else:
                logger.warning(f"[{self.sensor_type}] Fog returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"[{self.sensor_type}] Cannot reach fog node at {self.fog_node_url}")
        except requests.exceptions.Timeout:
            logger.error(f"[{self.sensor_type}] Fog node timed out")

    def run(self):
        """Thread entry point — continuously generate and dispatch readings."""
        logger.info(
            f"[{self.sensor_type}] Sensor {self.sensor_id} started on "
            f"segment {self.pipeline_segment} (interval: {self.dispatch_interval}s)"
        )
        while self.running:
            reading = self.generate_reading()
            payload = self.build_payload(reading)
            self.dispatch_to_fog(payload)
            time.sleep(self.dispatch_interval)

    def stop(self):
        """Gracefully stop the sensor thread."""
        self.running = False
        logger.info(f"[{self.sensor_type}] Sensor {self.sensor_id} stopped.")
