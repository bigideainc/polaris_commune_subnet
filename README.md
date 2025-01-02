
# Polaris Compute Subnet [NetUID 33]

Welcome to the **Polaris Compute Commune Subnet** repository. This project supports a decentralized AI ecosystem where miners provide compute resources to remote users, and validators ensure the integrity of the network. Below, you will find all the steps required to join and start contributing to the Polaris Compute Subnet (NetUID 33).

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Wallet Setup](#wallet-setup)
5. [Registration](#registration)
6. [Polar CLI Tool Configuration](#polar-cli-tool-configuration)
7. [Node Deployment](#node-deployment)
8. [Dashboard Monitoring](#dashboard-monitoring)
9. [Repository Setup](#repository-setup)
10. [Happy Mining](#happy-mining)

---

## Overview

Polaris Compute Subnet provides a platform for both miners and validators:

- **Miners** contribute compute resources, which are tracked and scored based on the quality and duration of the resources provided.
- **Validators** ensure the network’s security and reliability by maintaining ledger integrity and reward miners basing on their compute they provide to users.

**Note:** This guide assumes familiarity with Commune AI and Commune subnets.

---

## Prerequisites

- A system running **Windows** or **Linux** (no specific hardware requirements).
- Basic familiarity with command-line operations.
- COMAI tokens for registration:
  - Miners: 10 COMAI tokens.
  - Validators: At least 50 COMAI tokens (10 COMAI burned during registration).

---

## Installation

### Step 1: Install CommuneX

Run the following command to install CommuneX:

```bash
pip install communex
```

---

## Wallet Setup

### Step 2: Create a Wallet

Create a new wallet for your key using:

```bash
comx key create <your-key-name>
```

---

## Registration

### Step 3: Register on Polaris Compute Subnet (NetUID 33)

#### For Miners:

Register as a miner with the following command:

```bash
comx module register miner <your-key-name> 33
```

#### For Validators:

Ensure your account has at least 50 COMAI tokens before running the registration command:

```bash
comx module register validator <your-key-name> 33
```

---

## Polaris Setup

### Step 4: Clone the Repository

Install the Polar CLI tool using pip:

```bash
git clone https://github.com/bigideainc/polaris-subnet.git
cd polaris-subnet
```
### Step 5: Install Dependencies
Ensure you have Python 3.6 or higher installed. Then, install the required dependencies:
```bash
pip install -e .
```
### Step 6: Configure SSH Password
Polaris uses your machine's SSH password for secure connections. Add your SSH password to a .env file at the root of the project:
```bash
# .env file
SSH_PASSWORD=your_password_here
```
Note: The SSH password is used to configure and manage secure SSH tunnels between your machine and the Polaris compute network.

### Step 7: Start Polaris and Complete Registration

Start Polaris using:

```bash
polaris start
```

Register with Polaris by running:

```bash
polaris register
```

During registration:
- Select **Commune** as your registration type.
- Provide the wallet name you created.
- Follow the prompts to complete the registration.

### Step 8: Check Polaris Status

Ensure Polaris is running by checking its status:

```bash
polaris status
```

---

## Dashboard Monitoring

Verify that your node is active on the [Polaris Dashboard](https://polaris-dashboard-black.vercel.app/).

---

## Commune Repository Setup

### Step 9: Clone the Repository

Clone the Commune Polaris Compute Subnet repository:

```bash
git clone https://github.com/bigideainc/polaris_commune_subnet.git
cd polaris_commune_subnet
```

### Step 10: Set Up the Environment

Install Poetry:

```bash
pip install poetry
```

Activate the Poetry shell:

```bash
poetry shell
```

Install the necessary libraries:

```bash
pip install -e .
```

---

## Node Deployment

### Step 11: Run Your Node

#### For Miners:

Run the following command from the `polaris_commune_subnet` directory:

```bash
python3 polaris_subnet/cli.py miner <your-key-name> <ip> <port>
```

**Example:**

```bash
python3 polaris_subnet/cli.py miner yominer 127.0.0.1 8000
```

#### For Validators:

Run the following command from the `polaris_commune_subnet` directory:

```bash
python3 polaris_subnet/cli.py validator <your-key-name> <ip> <port>
```

**Example:**

```bash
python3 polaris_subnet/cli.py validator yominer 127.0.0.1 8000
```

---

## Happy Mining

You’re now part of the Commune AI Polaris Compute Subnet! Monitor your contributions, ensure your node’s uptime, and enjoy decentralized mining and validation.

---

For further assistance, feel free to reach out to our support team or consult the documentation. Happy Mining!