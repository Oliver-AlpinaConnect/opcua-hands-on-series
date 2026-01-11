# Raspberry Pi Modbus Monitoring & Fan Control Documentation

This documentation covers the setup, wiring, and execution of the Modbus-based environmental monitoring and fan control system.

## 1. Environment Setup

It is highly recommended to use a Python Virtual Environment (`venv`) to manage dependencies.

### Enable I2C Interface

Before proceeding, ensure the I2C interface is enabled on your Raspberry Pi:

1. Run `sudo raspi-config`.
2. Navigate to **Interface Options** > **I2C**.
3. Select **Yes** to enable.
4. Reboot the Pi if prompted.

### Virtual Environment Creation & Activation

Run the following commands in your project directory:

```bash
# Create a virtual environment
python3 -m venv --system-site-packages env

# Activate the virtual environment
source env/bin/activate
```

### Dependency Installation

Once the environment is active, install the required libraries:

```bash
pip install RPi.GPIO adafruit-circuitpython-bme680 pyModbusTCP
```

---

## 2. Hardware Pin Layout

The script uses **BCM Pin Numbering**. For the fan control, a transistor or relay is required as the GPIO pins cannot provide enough current to power a fan directly.

### Wiring Table

| Component | Function | Physical Pin | BCM / GPIO |
| :--- | :--- | :--- | :--- |
| **Fan** | Power (5V) | Pin 2 | 5V |
| **Fan** | Control Signal | Pin 13 | GPIO 27 |
| **BME680** | VCC (3.3V) | Pin 1 | 3.3V |
| **BME680** | Ground | Pin 9 | GND |
| **BME680** | SDA | Pin 3 | GPIO 2 (SDA) |
| **BME680** | SCL | Pin 5 | GPIO 3 (SCL) |

> **Note:** The Fan's positive lead connects to **Pin 2 (5V)**. The negative lead should be switched via a transistor (e.g., NPN) controlled by **GPIO 27**, ensuring a common ground with the Raspberry Pi.

---

## 3. Modbus Interface Summary

The application starts a Modbus TCP server on **Port 5020**.

### Register Logic

* **Holding Registers:** Used for all data.
* **Scaling:**
    * Temperature and Humidity values are multiplied by **10** (e.g., 25.5°C = 255).
    * Gas resistance is divided by **10**.
* **Hysteresis Control:** The fan turns ON when the CPU temperature exceeds `REG_THR_HIGH` and stays ON until it drops below `REG_THR_LOW`.

---

## 4. How to Run

1. **Activate the environment:**

```bash
source env/bin/activate
```

2. **Start the script:**

```bash
python modbus_interface.py
```

The console will confirm: Modbus Server started on 0.0.0.0:5020. To stop the server and clean up GPIO states, press CTRL+C.
