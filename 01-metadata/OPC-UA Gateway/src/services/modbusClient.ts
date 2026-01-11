import * as Modbus from 'jsmodbus';
import * as net from 'net';
import { MODBUS_CONFIG } from '../config/settings.js'; // Added .js

export class ModbusService {
    private socket = new net.Socket();
    public client = new Modbus.client.TCP(this.socket, MODBUS_CONFIG.unitId);
    public data: number[] = [];

    constructor() {
        this.socket.on('error', (err) => console.error(`[Modbus] Socket Error: ${err.message}`));
        this.socket.on('close', () => {
            console.log('[Modbus] Connection closed. Retrying in 5s...');
            setTimeout(() => this.connect(), 5000);
        });
    }

    connect() {
        console.log(`[Modbus] Connecting to ${MODBUS_CONFIG.host}...`);
        this.socket.connect({ host: MODBUS_CONFIG.host, port: MODBUS_CONFIG.port });
    }

    async startPolling() {
        setInterval(async () => {
            try {
                const response = await this.client.readHoldingRegisters(0, 36);
                this.data = response.response.body.values as number[];
            } catch (err) {
                console.error(`[Modbus] Polling Error: ${err}`);
            }
        }, MODBUS_CONFIG.pollingInterval);
    }
}

export const modbusService = new ModbusService();