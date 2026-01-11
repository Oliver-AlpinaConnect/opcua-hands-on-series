from dataclasses import dataclass

@dataclass
class SensorReadout:
    name: str
    value: float | bool
    unit: str
    source: str # "Modbus" or "OPC-UA"