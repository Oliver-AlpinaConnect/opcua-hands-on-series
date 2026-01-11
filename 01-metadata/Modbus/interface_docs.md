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

### General Information (Registers 0-9)

| Addr | Parameter     | Type | Scaling | Description                          |
| :--- | :------------ | :--- | :------ | :----------------------------------- |
| 0    | Version Major | UINT | 1       | **RO**: Software version major (e.g., 1)     |
| 1    | Version Minor | UINT | 1       | **RO**: Software version minor (e.g., 2)     |
| 2    | Uptime        | UINT | 1       | **RO**: Seconds since script started (0-65535)|

### BME680 Sensor Data (Registers 10-29)

| Addr | Parameter          | Type | Scaling | Description                          |
| :--- | :----------------- | :--- | :------ | :----------------------------------- |
| 10   | BME Temperature    | INT  | x 10    | **RO**: Ambient Temp (e.g., 254 = 25.4 °C)   |
| 11   | BME Humidity       | UINT | x 10    | **RO**: Relative Humidity (e.g., 452 = 45.2 %)|
| 12   | BME Gas Resistance | UINT | / 10    | **RO**: Gas resistance in Ohms / 10          |
| 13   | Sensor Control     | BOOL | 1/0     | **RW**: 1 = Enabled (Default) / 0 = Pause |

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
