# OPC UA Hands-On Series 🚀

This repository contains the source code, configuration files, and demonstration projects for the OPC UA Hands-On YouTube series. The goal of this series is to move beyond the theory and show how OPC UA simplifies industrial integration compared to legacy protocols.

To install the repository with git:

```bash
git clone https://github.com/Oliver-AlpinaConnect/opcua-hands-on-series.git
````

## 📺 Video Series Overview

### 01: Integrate Machines 10x Faster: The Power of OPC-UA

* **Topic:** Why OPC UA metadata makes vendor manuals obsolete.
* **Key Concepts:** Live Browsing, Metadata (Units/Ranges), and Self-Documentation.
* **Comparison:** Modbus TCP vs. OPC UA.
* **Watch Video:** [View on YouTube](https://www.youtube.com/watch?v=ndBl_vgoO1I)
* **Code Folder:** `/01-metadata`

### 02: OPC UA Security & Validation (Coming Soon)

* **Topic:** Implementing encryption, user authentication, and data validation (ranges/error handling).
* **Key Concepts:** Security Policies, Certificates (PKI), and EURange validation.
* **Watch Video:** [Link to be added upon release]
* **Code Folder:** `/02-security`

---

## 📂 Project Structure

The repository is organized by video chapters to help you follow along:

```text
OPCUA-HANDS-ON-SERIES/
├── 01-metadata/               # Video 1: Metadata & Browsing
│   ├── industrial-monitor/    # Frontend/App to display machine data
│   ├── Modbus/                # Legacy Modbus TCP simulation
│   └── OPC-UA Gateway/        # OPC UA Server providing context/metadata
├── 02-security/               # Video 2: Encryption & Auth
│   ├── modbus-app/            # Unsecured legacy example
│   └── opcua-app/             # Hardened OPC UA example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ Recommended Tools

To follow along with the demos without needing expensive industrial software, I recommend the following tools:

* **For Modbus Testing:** Use [ModbusTCP-CLI](https://github.com/Oliver-AlpinaConnect/modbustcp-cli) — a simple, free command-line tool to connect to Modbus TCP servers without needing to purchase dedicated software.
* **For OPC UA Browsing:** I use the [Prosys OPC UA Browser](https://prosysopc.com/products/opc-ua-browser/). It is a powerful, free tool for visualizing the address space and metadata of any OPC UA server.

---

## 🚀 Getting Started

### Prerequisites

* **Node.js** (for TypeScript/JavaScript projects)
* **Python 3.x** (for automation scripts)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/Oliver-AlpinaConnect/opcua-hands-on-series.git](https://github.com/Oliver-AlpinaConnect/opcua-hands-on-series.git)
    cd opcua-hands-on-series
    ```

2.  **Install Dependencies:**

    Navigate into the specific project folder you wish to run. For example:

    ```bash
    cd 01-metadata/OPC-UA-Gateway
    npm install
    ```

---

## 🤝 Contributing

If you find a bug or have a suggestion for a future video topic, feel free to open an **Issue** or submit a **Pull Request**.

**Created by Oliver @ AlpinaConnect**
