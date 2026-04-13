"""
Corrosion Rate Sensor Simulator
================================
Simulates ultrasonic wall thickness measurement in mm.

New pipe wall : 12.0 mm
Normal loss   : very slow degradation
Warning       : < 8.0 mm
Critical      : < 5.0 mm (high risk of rupture)
"""
import random
from .base_sensor import BaseSensor


class CorrosionSensor(BaseSensor):
    """Simulates ultrasonic pipeline wall thickness sensor (mm)."""

    def __init__(self, pipeline_segment: str, dispatch_interval: int = 10,
                 fog_node_url: str = 'http://127.0.0.1:8000/fog/ingest/'):
        # Corrosion changes slowly, so dispatch interval is slightly longer
        super().__init__(pipeline_segment, dispatch_interval, fog_node_url)
        self.sensor_type = 'CORROSION'
        # Start with a randomly degraded pipe to make dashboard interesting
        self._current_thickness = random.uniform(5.5, 11.5)

    def generate_reading(self) -> dict:
        """
        Generate Corrosion reading:
        - Very slow monotonic decrease (corrosion only gets worse over time)
        - Minor measurement noise
        """
        # Slow degradation (exaggerated slightly for simulation purposes)
        degradation = random.uniform(0.001, 0.01)
        self._current_thickness -= degradation

        # Sensor noise
        noise = random.gauss(0, 0.05)
        value = round(max(0.1, self._current_thickness + noise), 3)

        return {
            'value': value,
            'unit': 'mm',
            'metadata': {
                'status': 'CRITICAL' if value < 5.0 else ('WARNING' if value < 8.0 else 'NORMAL')
            }
        }
