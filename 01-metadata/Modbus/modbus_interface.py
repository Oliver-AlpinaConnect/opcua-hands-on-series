import time
import os
import board
import adafruit_bme680
import RPi.GPIO as GPIO
from pyModbusTCP.server import ModbusServer

# --- CONFIGURATION ---
VERSION_MAJOR = 1
VERSION_MINOR = 2
FAN_PIN = 27
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5020

# --- MODBUS MAP ---
# Holding Registers (HR)
REG_VERSION_MAJOR = 0
REG_VERSION_MINOR = 1
REG_UPTIME        = 2

REG_BME_TEMP      = 10  # Value * 10
REG_BME_HUM       = 11  # Value * 10
REG_BME_GAS       = 12  # Value / 10
REG_BME_CONTROL   = 13  # 1: Run, 0: Stop

REG_CPU_TEMP      = 30  # Value * 10
REG_THR_HIGH      = 31  # Default 550 (55.0 C)
REG_THR_LOW       = 32  # Default 450 (45.0 C)
REG_TEMP_STATUS   = 33  # 1 if Over High, 0 if Under Low
REG_FAN_STATUS    = 34  # 1: ON, 0: OFF
REG_MANUAL_FAN    = 35  # 1: Force ON, 0: Auto

# --- INITIALIZATION ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

try:
    i2c = board.I2C()
    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
except Exception as e:
    print(f"BME680 Init Error: {e}")
    sensor = None

server = ModbusServer(SERVER_IP, SERVER_PORT, no_block=True)

def get_cpu_temp():
    res = os.popen('vcgencmd measure_temp').readline()
    return float(res.replace("temp=","").replace("'C\n",""))

# --- START SERVER ---
server.start()
print(f"Modbus Server started on {SERVER_IP}:{SERVER_PORT}")

# Setup Default Thresholds
server.data_bank.set_holding_registers(REG_VERSION_MAJOR, [VERSION_MAJOR, VERSION_MINOR])
server.data_bank.set_holding_registers(REG_THR_HIGH, [550]) # 55.0 C
server.data_bank.set_holding_registers(REG_THR_LOW, [450])  # 45.0 C
server.data_bank.set_holding_registers(REG_BME_CONTROL, [1])
server.data_bank.set_holding_registers(REG_MANUAL_FAN, [0])

start_time = time.time()

try:
    while True:
        # 1. Update Uptime
        uptime = int(time.time() - start_time)
        server.data_bank.set_holding_registers(REG_UPTIME, [uptime % 65535])

        # 2. Read BME680 (if enabled)
        control = server.data_bank.get_holding_registers(REG_BME_CONTROL)[0]
        if control == 1 and sensor:
            server.data_bank.set_holding_registers(REG_BME_TEMP, [int(sensor.temperature * 10)])
            server.data_bank.set_holding_registers(REG_BME_HUM, [int(sensor.humidity * 10)])
            server.data_bank.set_holding_registers(REG_BME_GAS, [int(sensor.gas / 10)])

        # 3. CPU Fan Logic
        cpu_temp = get_cpu_temp()
        server.data_bank.set_holding_registers(REG_CPU_TEMP, [int(cpu_temp * 10)])
        
        high_thr = server.data_bank.get_holding_registers(REG_THR_HIGH)[0]
        low_thr = server.data_bank.get_holding_registers(REG_THR_LOW)[0]
        manual_mode = server.data_bank.get_holding_registers(REG_MANUAL_FAN)[0]
        
        current_temp_val = int(cpu_temp * 10)
        
        # Determine Status
        status = 0
        if current_temp_val >= high_thr:
            status = 1
        elif current_temp_val <= low_thr:
            status = 0
        else:
            # Keep previous status if between thresholds (Hysteresis)
            status = server.data_bank.get_holding_registers(REG_TEMP_STATUS)[0]
            
        server.data_bank.set_holding_registers(REG_TEMP_STATUS, [status])

        # Physical Control
        if manual_mode == 1 or status == 1:
            GPIO.output(FAN_PIN, GPIO.HIGH)
            server.data_bank.set_holding_registers(REG_FAN_STATUS, [1])
        else:
            GPIO.output(FAN_PIN, GPIO.LOW)
            server.data_bank.set_holding_registers(REG_FAN_STATUS, [0])

        time.sleep(1)

except KeyboardInterrupt:
    print("Shutting down...")
    GPIO.cleanup()
    server.stop()