import { modbusService } from "./services/modbusClient.js"; // Added .js
import { createOPCUAServer } from "./opcua/server.js"; // Added .js

async function main() {
    try {
        // 1. Start Modbus
        modbusService.connect();
        await modbusService.startPolling();

        // 2. Start OPC UA
        const server = await createOPCUAServer();
        await server.start();
        
        console.log(`✅ Server started: ${server.getEndpointUrl()}`);
    } catch (err) {
        console.error("Critical Start Error:", err);
    }
}

main();