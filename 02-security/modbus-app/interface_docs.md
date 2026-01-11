# Modbus TCP Interface Specification

## Raspberry Pi BME680 & Fan Control

### Server Configuration

| Parameter | Value |
| :------------- | :----------------------------- |
| **IP Address** | raspi3.local |
| **Port** | 5020 (Default) |
| **Slave ID** | 1 (Unit ID) |
| **Protocol** | Modbus TCP (Holding Registers) |

---

### Fan & CPU Control (Registers 30-49)

| Addr | Parameter       | Type | Scaling | Description                                  |
| :--- | :-------------- | :--- | :------ | :------------------------------------------- |
| 30   | CPU Temperature | INT  | x 10    | **RO**: Current RPi CPU Temp (e.g., 520 = 52.0°C)    |
| 31   | High Threshold  | UINT | x 10    | **RW**: Fan starts above this (Default: 550) |
| 32   | Low Threshold   | UINT | x 10    | **RW**: Fan stops below this (Default: 450)  |
| 33   | Temp Status     | BOOL | 1/0     | **RO**: 1 if Over High Thr / 0 if Under Low  |
| 34   | Fan Status      | BOOL | 1/0     | **RO**: 1 = Fan Running / 0 = Fan Stopped    |
| 35   | Manual Override | BOOL | 1/0     | **RW**: 1 = Force Fan ON / 0 = Auto Logic    |

### Implementation Notes

* **RW**: Read/Write (Control Register).
* **RO**: Read Only (Status/Sensor Register).
* **Data Scaling**: Since Modbus stores 16-bit integers, float values are multiplied by 10. 
* *Calculation:* `Real Value = Register Value / 10.0`
* **Gas Resistance**: Due to the high range of gas resistance, the value is divided by 10 to fit within a standard 16-bit UINT if necessary.
