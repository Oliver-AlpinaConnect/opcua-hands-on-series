import { DataType, standardUnits } from "node-opcua";

export interface ModbusVariableMetadata {
    browseName: string;
    description: string;
    register: number;
    dataType: DataType;
    scaling?: number;
    isWritable?: boolean;
    unit?: keyof typeof standardUnits;
    range?: { min: number; max: number };
    precision?: number;
    category: 'General' | 'Environment' | 'FanControl';
}

export const VARIABLE_DEFINITIONS: ModbusVariableMetadata[] = [
    // --- General Info ---
    {
        browseName: "Version_Major",
        description: "Software version major number",
        register: 0,
        dataType: DataType.UInt16,
        category: 'General'
    },
    {
        browseName: "Version_Minor",
        description: "Software version minor number",
        register: 1,
        dataType: DataType.UInt16,
        category: 'General'
    },
    {
        browseName: "Uptime",
        description: "Total seconds elapsed since the script started",
        register: 2,
        dataType: DataType.UInt32,
        unit: "second",
        category: 'General'
    },

    // --- BME680 Environment Data ---
    {
        browseName: "BME_Temperature",
        description: "Ambient temperature from the BME680 sensor",
        register: 10,
        dataType: DataType.Double,
        scaling: 10,
        unit: "degree_celsius",
        range: { min: -40, max: 85 },
        precision: 1,
        category: 'Environment'
    },
    {
        browseName: "BME_Humidity",
        description: "Relative humidity percentage",
        register: 11,
        dataType: DataType.Double,
        scaling: 10,
        unit: "percent",
        range: { min: 0, max: 100 },
        precision: 1,
        category: 'Environment'
    },
    {
        browseName: "BME_Gas_Resistance",
        description: "Air quality/Gas resistance in Ohms",
        register: 12,
        dataType: DataType.Double,
        scaling: 0.1, // Note: In logic, this divides raw by 0.1 (effectively x10)
        range: { min: 0, max: 1000000 },
        category: 'Environment'
    },
    {
        browseName: "Sensor_Control",
        description: "Enable (1) or Pause (0) BME680 sensor reading updates",
        register: 13,
        dataType: DataType.Boolean,
        isWritable: true,
        category: 'Environment'
    },

    // --- Fan & CPU Control ---
    {
        browseName: "CPU_Temperature",
        description: "Current Raspberry Pi SoC Temperature",
        register: 30,
        dataType: DataType.Double,
        scaling: 10,
        range: { min: 0, max: 75 },
        unit: "degree_celsius",
        precision: 1,
        category: 'FanControl'
    },
    {
        browseName: "High_Threshold",
        description: "Fan starts automatically above this temperature",
        register: 31,
        dataType: DataType.Double,
        scaling: 10,
        range: { min: 0, max: 60 },
        isWritable: true,
        unit: "degree_celsius",
        precision: 1,
        category: 'FanControl'
    },
    {
        browseName: "Low_Threshold",
        description: "Fan stops automatically below this temperature",
        register: 32,
        dataType: DataType.Double,
        scaling: 10,
        range: { min: 0, max: 50 },
        isWritable: true,
        unit: "degree_celsius",
        precision: 1,
        category: 'FanControl'
    },
    {
        browseName: "Temp_Status",
        description: "Threshold status: 1 if Over High Thr / 0 if Under Low",
        register: 33,
        dataType: DataType.Boolean,
        category: 'FanControl'
    },
    {
        browseName: "Fan_Status",
        description: "Current physical state of the fan (1 = Running / 0 = Stopped)",
        register: 34,
        dataType: DataType.Boolean,
        category: 'FanControl'
    },
    {
        browseName: "Manual_Override",
        description: "1 = Force Fan ON / 0 = Follow automatic logic",
        register: 35,
        dataType: DataType.Boolean,
        isWritable: true,
        category: 'FanControl'
    }
];