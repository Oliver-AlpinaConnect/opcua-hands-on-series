import { 
    OPCUAServer, OPCUACertificateManager, SecurityPolicy, 
    MessageSecurityMode, DataType, Variant, Range, 
    AccessLevelFlag, makeAccessLevelFlag, standardUnits, StatusCodes 
} from "node-opcua";
import * as path from "path";
import { OPCUA_CONFIG } from "../config/settings.js"; // Added .js
import { VARIABLE_DEFINITIONS, ModbusVariableMetadata } from "./variables.js"; // Added .js
import { modbusService } from "../services/modbusClient.js"; // Added .js

export async function createOPCUAServer() {
    const server = new OPCUAServer({
        port: OPCUA_CONFIG.port,
        resourcePath: OPCUA_CONFIG.resourcePath,
        serverCertificateManager: new OPCUACertificateManager({
            rootFolder: path.join(process.cwd(), "certificates/pki"),
            automaticallyAcceptUnknownCertificate: true
        }),
        securityPolicies: [SecurityPolicy.None, SecurityPolicy.Basic256Sha256],
        securityModes: [MessageSecurityMode.None, MessageSecurityMode.SignAndEncrypt],
        userManager: {
            isValidUser: (u: string, p: string) => u === "admin" && p === "password"
        }
    });

    await server.initialize();
    const addressSpace = server.engine.addressSpace!;
    const namespace = addressSpace.getOwnNamespace();

    // Create Folders
    const folders = {
        General: namespace.addObject({ organizedBy: addressSpace.rootFolder.objects, browseName: "RPi_General_Info" }),
        Environment: namespace.addObject({ organizedBy: addressSpace.rootFolder.objects, browseName: "RPi_Environment_Sensor" }),
        FanControl: namespace.addObject({ organizedBy: addressSpace.rootFolder.objects, browseName: "RPi_Fan_Control" }),
    };

    // Helper to bind variables
    const bindVariable = (meta: ModbusVariableMetadata) => {
        const parent = folders[meta.category];
        const unitInfo = meta.unit ? standardUnits[meta.unit] : null;

        const node = namespace.addAnalogDataItem({
            componentOf: parent,
            browseName: meta.browseName,
            description: meta.description,
            dataType: meta.dataType,
            accessLevel: meta.isWritable ? "CurrentRead | CurrentWrite" : "CurrentRead",
            engineeringUnits: unitInfo || undefined,
            engineeringUnitsRange: meta.range ? new Range({ low: meta.range.min, high: meta.range.max }) : undefined,
        });

        node.bindVariable({
            get: () => {
                const raw = modbusService.data[meta.register] ?? 0;
                const val = meta.dataType === DataType.Boolean ? raw === 1 : raw / (meta.scaling || 1);
                return new Variant({ dataType: meta.dataType, value: val });
            },
            set: meta.isWritable ? (variant: Variant) => {
                const toWrite = meta.dataType === DataType.Boolean ? (variant.value ? 1 : 0) : Math.round(variant.value * (meta.scaling || 1));
                modbusService.client.writeSingleRegister(meta.register, toWrite);
                return StatusCodes.Good;
            } : undefined
        }, true);
    };

    VARIABLE_DEFINITIONS.forEach(bindVariable);
    return server;
}