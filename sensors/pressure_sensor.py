"""
Pressure Sensor Simulator
==========================
Simulates pipeline pressure readings (PSI) for a given segment.

Normal operating range : 400–500 PSI
Warning range          : 350–400 / 500–550 PSI
Critical               : <350 PSI (pipe burst / leak) or >550 PSI (over-pressure)

A random 5% chance of a sudden pressure drop simulates a pipe burst event.
"""
import random
from .base_sensor import BaseSensor


class PressureSensor(BaseSensor):
    """Simulates pipeline pressure sensor (PSI)."""

    # Operating thresholds (PSI)
    NORMAL_MIN  = 400
    NORMAL_MAX  = 500
    WARNING_LOW = 350
    WARNING_HI  = 550
    BASE_PSI    = 450  # Nominal operating pressure

    def __init__(self, pipeline_segment: str, dispatch_interval: int = 3,
                 fog_node_url: str = 'http://127.0.0.1:8000/fog/ingest/'):
        super().__init__(pipeline_segment, dispatch_interval, fog_node_url)
        self.sensor_type = 'PRESSURE'
        self._current_psi = self.BASE_PSI  # Track for gradual drift

    def generate_reading(self) -> dict:
        """
        Generate a realistic pressure reading with:
        - Natural Gaussian noise (~±3 PSI)
        - Gradual drift over time
        - 5% chance of sudden burst (pressure drop)
        - 2% chance of over-pressure spike
        """
        # Natural fluctuation
        noise = random.gauss(0, 2.5)

        # Gradual drift (slow trend)
        drift = random.uniform(-0.5, 0.5)
        self._current_psi = max(300, min(600, self._current_psi + drift))

        # Anomaly events
        burst_event      = random.random() < 0.05  # 5%  → pipe burst (pressure drop)
        overpressure_event = random.random() < 0.02  # 2% → over-pressure

        if burst_event:
            value = self._current_psi - random.uniform(60, 120)
        elif overpressure_event:
            value = self._current_psi + random.uniform(60, 100)
        else:
            value = self._current_psi + noise

        value = round(max(200, min(700, value)), 2)

        return {
            'value': value,
            'unit': 'PSI',
            'metadata': {
                'burst_event'      : burst_event,
                'overpressure_event': overpressure_event,
                'baseline_psi'     : round(self._current_psi, 2),
            }
        }
