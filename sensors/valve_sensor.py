"""
Valve Position Sensor Simulator
================================
Simulates the open/close percentage of pipeline valves.

Normal : 100% (fully open)
Partial: 1-99% (throttled)
Closed : 0% (shut down)
"""
import random
from .base_sensor import BaseSensor


class ValveSensor(BaseSensor):
    """Simulates valve position sensor (%)."""

    def __init__(self, pipeline_segment: str, dispatch_interval: int = 3,
                 fog_node_url: str = 'http://127.0.0.1:8000/fog/ingest/'):
        super().__init__(pipeline_segment, dispatch_interval, fog_node_url)
        self.sensor_type = 'VALVE_POS'
        self._current_position = 100.0  # Open by default

    def generate_reading(self) -> dict:
        """
        Generate Valve Position reading.
        Occasionally valves are throttled slightly.
        """
        throttle_event = random.random() < 0.05
        
        if throttle_event:
            # Drop to somewhere between 80-95% briefly
            self._current_position = random.uniform(80.0, 95.0)
        else:
            # Creep back up to 100%
            self._current_position = min(100.0, self._current_position + random.uniform(1.0, 5.0))
            
        value = round(self._current_position, 1)

        return {
            'value': value,
            'unit': '%',
            'metadata': {
                'status': 'CLOSED' if value == 0 else ('PARTIAL' if value < 100 else 'OPEN')
            }
        }
