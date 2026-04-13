"""
H2S Gas Sensor Simulator
=========================
Simulates Hydrogen Sulfide (H2S) gas levels in Parts Per Million (PPM).
H2S is a highly toxic gas common in oil/gas extraction.

Normal range : 0 - 5 PPM
Warning range: 5 - 10 PPM
Critical     : >10 PPM (requires immediate evacuation/shutoff)
"""
import random
from .base_sensor import BaseSensor


class H2SGasSensor(BaseSensor):
    """Simulates H2S gas leak detection sensor (PPM)."""

    def __init__(self, pipeline_segment: str, dispatch_interval: int = 3,
                 fog_node_url: str = 'http://127.0.0.1:8000/fog/ingest/'):
        super().__init__(pipeline_segment, dispatch_interval, fog_node_url)
        self.sensor_type = 'H2S_GAS'
        self._current_ppm = 1.0

    def generate_reading(self) -> dict:
        """
        Generate H2S PPM reading:
        - Usually stays very low (0-3 PPM)
        - 3% chance of a sudden hazardous gas leak spike (>10 PPM)
        """
        # Gas levels tend to stay low unless there's a leak
        if self._current_ppm > 3.0:
            # Gradually dissipate gas if it was high
            self._current_ppm *= 0.8
        else:
            self._current_ppm = random.uniform(0.5, 2.5)

        leak_event = random.random() < 0.03  # 3% chance of dangerous leak

        if leak_event:
            self._current_ppm = random.uniform(11.0, 50.0)

        value = round(max(0.0, self._current_ppm + random.gauss(0, 0.5)), 2)

        return {
            'value': value,
            'unit': 'PPM',
            'metadata': {
                'leak_event': leak_event,
                'hazard_level': 'CRITICAL' if value > 10 else ('WARNING' if value > 5 else 'SAFE')
            }
        }
