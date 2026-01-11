#!/bin/bash
set -e

echo "🚀 Starting OPC-UA Gateway Setup on Raspberry Pi..."

# 1. System Updates & Essential Libraries
# build-essential: Required for some npm packages to build native modules
echo "--- Installing system dependencies ---"
sudo apt update
sudo apt install -y build-essential curl

# 2. Install Node.js (LTS Version 22)
if ! command -v node &> /dev/null; then
    echo "--- Installing Node.js v22 ---"
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo "--- Node.js already installed ($(node -v)) ---"
fi

# 3. Project Dependency Installation
# This script assumes package.json and tsconfig.json are present in the directory.
# It will install dependencies, then build the project.
echo "--- Installing NPM packages from package.json ---"
npm install

echo "--- Building TypeScript project ---"
npm run build

echo "-------------------------------------------------------"
echo "✅ SETUP COMPLETE"
echo "-------------------------------------------------------"
echo ""
echo "The project has been set up and built."
echo ""
echo "To run the server, use:"
echo "npm start"
echo ""
echo "For development, you can use:"
echo "npm run dev"
echo ""