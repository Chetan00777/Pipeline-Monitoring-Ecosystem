"""
Flow Rate Sensor Simulator
===========================
Simulates the flow rate of oil/gas entirely entirely through a segment (Litres/Min).

Normal flow : 1000 - 1200 L/min
Low flow    : < 800 L/min (potentially a blockage or upstream leak)
High flow   : > 1400 L/min (surge)
"""
import random
from .base_sensor import BaseSensor


class FlowRateSensor(BaseSensor):
    """Simulates fluid flow rate sensor (L/min)."""

    def __init__(self, pipeline_segment: str, dispatch_interval: int = 3,
                 fog_node_url: str = 'http://127.0.0.1:8000/fog/ingest/'):
        super().__init__(pipeline_segment, dispatch_interval, fog_node_url)
        self.sensor_type = 'FLOW_RATE'
        self._current_flow = 1100.0

    def generate_reading(self) -> dict:
        """
        Generate Flow Rate reading:
        - Natural fluctuation around 1100 L/min
        - 4% chance of flow drop (blockage/leak)
        """
        noise = random.gauss(0, 15.0)
        self._current_flow = max(900.0, min(1300.0, self._current_flow + random.uniform(-10, 10)))
        
        flow_drop_event = random.random() < 0.04
        
        if flow_drop_event:
            value = self._current_flow - random.uniform(300, 500)
        else:
            value = self._current_flow + noise
            
        value = round(max(0.0, value), 2)
        
        return {
            'value': value,
            'unit': 'L/min',
            'metadata': {
                'anomaly': flow_drop_event,
                'status': 'WARNING' if (value < 800 or value > 1400) else 'NORMAL'
            }
        }
