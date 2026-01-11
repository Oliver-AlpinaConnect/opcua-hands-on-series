import asyncio
import random
import os
import platform  # Useful for detecting the OS

from pymodbus.server import StartAsyncTcpServer as modbus_server 
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.pdu import ExceptionResponse
from pymodbus.constants import ExcCodes

# --- CONDITIONAL GPIO IMPORT ---
try:
    import RPi.GPIO as GPIO
    IS_RASPI = True
    print("Running on Raspberry Pi: Real GPIO enabled.")
except (ImportError, RuntimeError):
    IS_RASPI = False
    print("RPi.GPIO not found. Running in SIMULATION mode.")

    # Create a Mock GPIO class to prevent NameErrors on Mac
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, state): 
            # Optional: print state changes for debugging on Mac
            # print(f"[SIM] GPIO {pin} set to {state}")
            pass
        def cleanup(self): pass

    GPIO = MockGPIO()

# --- CONFIGURATION (Protocol Addresses / 0-indexed) ---
FAN_PIN = 27
REG_CPU_TEMP    = 30 + 1  # Read-Only for Client
REG_THR_HIGH    = 31 + 1  # R/W - Max 65.0 C
REG_THR_LOW     = 32 + 1  # R/W - Max 55.0 C
REG_TEMP_STATUS = 33 + 1  # Read-Only for Client
REG_FAN_STATUS  = 34 + 1  # Read-Only for Client
REG_MANUAL_FAN  = 35 + 1  # R/W - (0 or 1)

# --- CUSTOM VALIDATION LOGIC ---
class ValidatingDataBlock(ModbusSparseDataBlock):
    def setValues(self, address, values):
        """
        Intercepts EXTERNAL Modbus network writes.
        """
        for i, val in enumerate(values):
            current_addr = address + i

            # 1. Protect Read-Only Registers from External Clients
            if current_addr in [REG_CPU_TEMP, REG_TEMP_STATUS, REG_FAN_STATUS]:
                print(f"REJECTED: External attempt to write read-only register {current_addr}")
                return ExcCodes.ILLEGAL_FUNCTION
            
            # 2. Threshold Validation
            if current_addr == REG_THR_HIGH and val > 650:
                print(f"REJECTED: {val/10}°C exceeds High Max (65.0°C)")
                return ExcCodes.ILLEGAL_VALUE
            
            if current_addr == REG_THR_LOW and val > 550:
                print(f"REJECTED: {val/10}°C exceeds Low Max (55.0°C)")
                return ExcCodes.ILLEGAL_VALUE

            # 3. Mode Validation
            if current_addr == REG_MANUAL_FAN and val not in [0, 1]:
                print(f"REJECTED: Invalid Manual Fan value {val}")
                return ExcCodes.ILLEGAL_VALUE

        return super().setValues(address, values)

    def set_internal(self, address, values):
        """
        Bypass method for the server's internal logic loop.
        """
        return super().setValues(address, values)

# --- HARDWARE & LOGIC ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

def get_cpu_temp():
    """
    Tries to read real Pi temp, falls back to simulation.
    """
    if IS_RASPI:
        try:
            res = os.popen('vcgencmd measure_temp').readline()
            return float(res.replace("temp=","").replace("'C\n",""))
        except Exception:
            pass
    
    # Fallback/Simulation mode
    return random.randint(400, 700)

async def run_fan_logic(context):
    slave_id = 0x00
    # Access the holding register block directly for internal updates
    hr_block = context[slave_id].store['h']

    while True:
        try:
            cpu_temp = get_cpu_temp()
            
            # Use set_internal to update Read-Only registers internally
            hr_block.set_internal(REG_CPU_TEMP, [cpu_temp])

            # Read settings
            high_thr = hr_block.getValues(REG_THR_HIGH, 1)[0]
            low_thr = hr_block.getValues(REG_THR_LOW, 1)[0]
            manual = hr_block.getValues(REG_MANUAL_FAN, 1)[0]
            status = hr_block.getValues(REG_TEMP_STATUS, 1)[0]

            # Hysteresis Logic
            if cpu_temp >= high_thr:
                status = 1
            elif cpu_temp <= low_thr:
                status = 0
            
            hr_block.set_internal(REG_TEMP_STATUS, [status])

            # Logic Control
            if manual == 1 or status == 1:
                GPIO.output(FAN_PIN, GPIO.HIGH)
                hr_block.set_internal(REG_FAN_STATUS, [1])
            else:
                GPIO.output(FAN_PIN, GPIO.LOW)
                hr_block.set_internal(REG_FAN_STATUS, [0])
                
        except Exception as e:
            print(f"Logic Error: {e}")
        await asyncio.sleep(1)

async def main():
    # Initialize block from address 0 to ensure mapping matches constants
    block = ValidatingDataBlock({addr: 0 for addr in range(0, 100)})
    store = ModbusDeviceContext(hr=block)
    context = ModbusServerContext(store, single=True)

    # Initialize defaults via the internal bypass
    block.set_internal(REG_THR_HIGH, [550])
    block.set_internal(REG_THR_LOW, [450])

    asyncio.create_task(run_fan_logic(context))

    print("Starting Modbus Server on 0.0.0.0:5020...")
    await modbus_server(
        context=context, 
        address=("0.0.0.0", 5020)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        GPIO.cleanup() # This now works on both Mac (does nothing) and Pi (cleans up)