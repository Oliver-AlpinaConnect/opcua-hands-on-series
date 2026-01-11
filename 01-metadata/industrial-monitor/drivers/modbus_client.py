from pymodbus.client import ModbusTcpClient
from .base import SensorReadout

class ModbusDriver:
    def __init__(self, config, tags):
        self.client = ModbusTcpClient(config['host'], port=config['port'])
        self.tags = tags
        self.device_id = config['device_id']

    def read_all(self):
        results = []
        if not self.client.connected:
            self.client.connect()
            
        for tag in self.tags:
            resp = self.client.read_holding_registers(
                address=tag['register'], 
                count=1, 
                device_id=self.device_id
            )
            
            if not resp.isError():
                raw = resp.registers[0]
                # MANUAL SCALING AND TYPING
                value = raw * tag.get('scale', 1.0)
                
                if tag.get('type') == 'bool':
                    value = bool(raw)
                
                results.append(SensorReadout(
                    name=tag['name'],
                    value=value,
                    unit=tag['unit'],
                    source="Modbus"
                ))
        return results