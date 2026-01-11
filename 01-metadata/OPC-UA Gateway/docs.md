# OPC-UA Gateway Documentation

This document provides instructions on how to set up, install, and run the OPC-UA Gateway application on a Raspberry Pi or other Debian-based Linux system.

## 1. Overview

The OPC-UA Gateway acts as a bridge between a Modbus-enabled device and an OPC-UA client. It reads data from a Modbus TCP server and exposes it through an OPC-UA server, allowing modern clients to monitor and interact with legacy industrial devices.

## 2. Prerequisites

Before you begin, ensure you have the following:
- A Raspberry Pi (or other compatible device) with a fresh installation of Raspberry Pi OS (or another Debian-based distribution).
- An internet connection on the device.
- `git` installed to clone the repository.
- Physical or network access to the device's terminal.

## 3. Setup and Installation

The setup process is automated via a shell script.

**Run the Setup Script:**
    Navigate to the `OPC-UA Gateway` directory and execute the setup script. This script will:
    - Install essential system libraries (`build-essential`, `curl`).
    - Install Node.js (v22).
    - Install all necessary project dependencies using `npm`.
    - Build the TypeScript project.

    ```bash
    cd "OPC-UA Gateway"
    chmod +x setup.sh
    ./setup.sh
    ```
    The script requires `sudo` privileges for system-wide installations and will prompt for your password.

## 4. Running the Application

Once the setup is complete, you can run the gateway in two modes (**Note**: Don't forget to start the Modbus interface. Alternative, you can use the script mentioned below.):

-   **Production Mode:**
    This command runs the compiled JavaScript code from the `dist` directory. It's the recommended way to run the application for stable, long-term use.

    ```bash
    npm start
    ```

-   **Development Mode:**
    This command uses `ts-node` to run the TypeScript code directly from the `src` directory. It's useful for development and debugging, as it doesn't require a separate build step after making code changes.

    ```bash
    npm run dev
    ```

-   **Gateway with Modbus Interface:**
    This command starts both the Modbus interface and the OPC-UA Gateway. It is the recommended way to run the application if the Modbus device is on the same machine.

    ```bash
    chmod +x start_gateway.sh
    ./start_gateway.sh
    ```

Upon a successful start, you will see a message in the console indicating that the server is running and listening on its configured endpoint, which defaults to `opc.tcp://<hostname>:4840/UA/RPiServer`.

## 5. Configuration

The application's behavior can be modified through the settings file located at `src/config/settings.ts`.

-   `MODBUS_CONFIG`: Contains settings for the Modbus TCP server connection, such as `host`, `port`, and `pollingInterval`.
-   `OPCUA_CONFIG`: Contains settings for the OPC-UA server, including `port` and `resourcePath`.

Modify these values as needed to match your environment. Remember to rebuild the project (`npm run build`) after making changes if you intend to run it in production mode.
