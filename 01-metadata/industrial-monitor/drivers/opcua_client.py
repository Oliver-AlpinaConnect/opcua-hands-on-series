from asyncua import Client
from .base import SensorReadout

class OpcUaDriver:
    def __init__(self, config, tags):
        self.url = config['url']
        self.tags = tags
        self.client = Client(url=self.url)

    async def read_all(self):
        results = []
        try:
            async with self.client:
                for tag in self.tags:
                    node = self.client.get_node(tag['node_id'])
                    val = await node.get_value()
                    # We can even fetch the unit from the server if we wanted!
                    results.append(SensorReadout(
                        name=tag['name'],
                        value=val,
                        unit="", # Let's assume units are part of the value or handled in UI
                        source="OPC-UA"
                    ))
        except Exception:
            pass # Handle connection errors
        return results