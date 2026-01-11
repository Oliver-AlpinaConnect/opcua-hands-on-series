import asyncio
import logging
from asyncua import ua, Server
from hardware import PiHardware
from user_manager import FanUserManager, Ruleset, change_user_access_level
from asyncua.common.callback import CallbackType

logging.basicConfig(level=logging.INFO)

LIMIT_HIGH_THRESHOLD = 65.0  # °C
LIMIT_LOW_THRESHOLD = 55.0   # °C

async def validate_thresholds(event, dispatcher):
    # event.user is the user object from your UserManager
    # event.request_params contains the WriteValue objects
    for write_value in event.request_params.NodesToWrite:
        node_id = write_value.NodeId
        new_val = write_value.Value.Value.Value  # Extract the actual python value

        # Check HighThreshold (e.g., must be between 0.0 and 60.0)
        if "HighThreshold" in str(node_id):
            if not (0.0 <= new_val <= LIMIT_HIGH_THRESHOLD):
                logging.warning(f"Rejected HighThreshold write: {new_val}")
                raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)

        # Check LowThreshold (e.g., must be between 0.0 and 50.0)
        elif "LowThreshold" in str(node_id):
            if not (0.0 <= new_val <= LIMIT_LOW_THRESHOLD):
                logging.warning(f"Rejected LowThreshold write: {new_val}")
                raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)

async def main():
    user_manager = FanUserManager()
    server = Server(user_manager=user_manager)
    await server.init()

    app_uri = "urn:fan:control:opc-ua:server"
    ns = await server.register_namespace(app_uri)

    obj = await server.nodes.objects.add_object(ns, "FanControl")

    # Prepare helpers for metadata
    #--------------------------------
    temp_unit = ua.EUInformation()
    temp_unit.DisplayName = ua.LocalizedText("°C")
    temp_unit.Description = ua.LocalizedText("Degree Celsius")
    temp_unit.UnitId = 4408652 
    temp_unit.NamespaceUri = "http://www.opcfoundation.org/UA/units/un/cefact"

    # Adding Variables
    #--------------------------------
    # Read-Only Nodes
    cpu_temp = await obj.add_variable(
        ua.NodeId("CPUTemperature", ns),
        "CPUTemperature",
        0.0
    )
    await cpu_temp.add_property(ns, "EURange", ua.Range(Low=0.0, High=75.0))
    await cpu_temp.add_property(ns, "EngineeringUnits", temp_unit)
    await cpu_temp.write_attribute(
        ua.AttributeIds.DisplayName, 
        ua.DataValue(ua.LocalizedText("CPU Temperature [°C]"))
    )
    await cpu_temp.write_attribute(
        ua.AttributeIds.Description, 
        ua.DataValue(ua.LocalizedText("Actual temperature of the CPU in degree Celsius."))
    )

    overheat_status = await obj.add_variable(ns, "OverheatStatus", False)
    await overheat_status.write_attribute(
        ua.AttributeIds.Description, 
        ua.DataValue(ua.LocalizedText("Status of the Overheat condition (true -> overheat, cpu temp over high threshold / false -> normal)"))
    )

    fan_status = await obj.add_variable(ns, "FanStatus", False)
    await fan_status.write_attribute(
        ua.AttributeIds.Description, 
        ua.DataValue(ua.LocalizedText("Status of the FAN (true -> running / false -> stopped)"))
    )
    
    # Read-Write Nodes (Protected by CustomAccessProvider)
    high_thr = await obj.add_variable(
        ua.NodeId("HighThreshold", ns),
        "HighThreshold",
        0.0
    )
    await high_thr.set_writable()
    await high_thr.add_property(ns, "EURange", ua.Range(Low=0.0, High=LIMIT_HIGH_THRESHOLD))
    await high_thr.add_property(ns, "EngineeringUnits", temp_unit)
    await high_thr.write_attribute(
        ua.AttributeIds.DisplayName, 
        ua.DataValue(ua.LocalizedText("High Threshold [°C]"))
    )
    await high_thr.write_attribute(
        ua.AttributeIds.Description, 
        ua.DataValue(ua.LocalizedText("Upper limit for fan activation"))
    )

    low_thr = await obj.add_variable(
        ua.NodeId("LowThreshold", ns),
        "LowThreshold",
        0.0
    )
    await low_thr.write_attribute(
        ua.AttributeIds.DisplayName, 
        ua.DataValue(ua.LocalizedText("Low Threshold [°C]"))
    )
    await low_thr.write_attribute(
        ua.AttributeIds.Description, 
        ua.DataValue(ua.LocalizedText("Lower limit for fan deactivation"))
    )
    await low_thr.set_writable()
    await low_thr.add_property(ns, "EURange", ua.Range(Low=0.0, High=LIMIT_LOW_THRESHOLD))
    await low_thr.add_property(ns, "EngineeringUnits", temp_unit)
    
    manual_ovr = await obj.add_variable(ns, "ManualOverride", False)
    await manual_ovr.set_writable()
    await manual_ovr.write_attribute(
        ua.AttributeIds.Description, 
        ua.DataValue(ua.LocalizedText("Overrides the control logic (true -> fan runs no matter the CPU temperature / false -> fan runs based on internal logic)"))
    )
    #--------------------------------

    server.set_endpoint("opc.tcp://0.0.0.0:4840/pi/fan/")
    server.set_server_name("RPi Fan Control Server")

    # Load security (ensure you ran create_certs.py)
    try:
        await server.load_certificate("certs/server_cert.der")
        await server.load_private_key("certs/server_key.pem")
    except FileNotFoundError:
        logging.error("Missing certs! Run create_certs.py first.")
        return

    # Apply tokens
    server.set_identity_tokens(
        [
            ua.AnonymousIdentityToken, 
            ua.X509IdentityToken, 
            ua.UserNameIdentityToken
        ]
    )

    # 2. Security Policies
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ],
        Ruleset() 
    )

    server.subscribe_server_callback(CallbackType.PostRead, change_user_access_level)
    server.subscribe_server_callback(CallbackType.PreWrite, validate_thresholds)
    
    hw = PiHardware()
    # 4. START SERVER
    async with server:
        logging.info("Server is running...")
        await low_thr.write_value(hw.get_low_threshold())
        await high_thr.write_value(hw.get_high_threshold())
        await manual_ovr.write_value(hw.get_manual_override())
        # intial write of variables
        while True:
            # 1. READ values from the OPC UA Server (in case a client changed them)
            # This ensures the Hardware object stays in sync with the UA Interface 
            current_low = await low_thr.read_value()
            current_high = await high_thr.read_value()
            current_manual = await manual_ovr.read_value()

            hw.set_low_threshold(current_low)
            hw.set_high_threshold(current_high)
            hw.set_manual_override(current_manual)

            # 2. READ actual CPU temperature from hardware
            act_cpu_temp = hw.get_cpu_temp()
            await cpu_temp.write_value(act_cpu_temp)

            # 3. RUN the Hysteresis Logic
            # We call the internal hardware method that checks the thresholds
            hw.fan_control(act_cpu_temp)

            # 4. UPDATE the Fan Status in OPC UA so clients can see it
            # Using _fan_state from the hardware class
            await fan_status.write_value(hw.get_fan_state())            
            await overheat_status.write_value(hw.get_overheat_state())
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())