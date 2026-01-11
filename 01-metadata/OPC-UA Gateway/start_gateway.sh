#!/bin/bash

# Start the Modbus interface in the background
echo "Starting Modbus interface..."
source ../Modbus/venv/bin/activate
python3 ../Modbus/modbus_interface.py &

# Give the Modbus server some time to start
sleep 5

# Start the OPC-UA Gateway
echo "Starting OPC-UA Gateway..."
npm start
