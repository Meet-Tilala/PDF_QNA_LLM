# Lab Assignment 9 – Network Simulation using OMNet++

**Course:** Computer Networks Lab  
**Author:** Meet Tilala | B23CS1036  
**Institute:** Indian Institute of Technology Jodhpur

---

## Overview

This project simulates a simple network with **2 hosts** and **1 router** using OMNet++ (Objective Modular Network Testbed in C++). HostA sends 5 packets to HostB through a central router. Each network link has a propagation delay of 100ms.

---

## Project Structure

```
Lab9/
├── src/
│   ├── Network.ned     # Network topology definition
│   ├── Host.h          # Host module declaration
│   ├── Host.cc         # Host module implementation
│   ├── Router.h        # Router module declaration
│   └── Router.cc       # Router module implementation
├── omnetpp.ini         # Simulation configuration
└── README.md           # This file
```

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| OMNet++     | 6.x (recommended) or 5.7+ |
| C++ Compiler | g++ 9+ or clang++ |
| OS | Linux / Windows / macOS |

Download OMNet++ from: https://omnetpp.org/download/

---

## Setup & Running

### Step 1 – Import the Project

1. Launch the OMNet++ IDE (Eclipse-based).
2. Go to **File → New → OMNet++ Project**.
3. Name the project `Lab9`.
4. Copy all files from `src/` into the project's `src/` folder.
5. Place `omnetpp.ini` in the project root.

### Step 2 – Build

In the OMNet++ IDE:
- Right-click the project → **Build Project**

Or via terminal:
```bash
cd Lab9
opp_makemake -f --deep
make
```

### Step 3 – Run (GUI Mode)

1. Right-click `omnetpp.ini` → **Run As → OMNet++ Simulation**
2. The Qtenv GUI will open showing the network topology.
3. Press the **Run** or **Fast Run** button.

### Step 4 – Run (Command Line / Cmdenv)

```bash
./Lab9 -u Cmdenv -f omnetpp.ini
```

---

## Expected Output

```
HostA sending packet 1 to HostB
Router forwarding packet...
Message received at hostB
HostA sending packet 2 to HostB
Router forwarding packet...
Message received at hostB
HostA sending packet 3 to HostB
Router forwarding packet...
Message received at hostB
HostA sending packet 4 to HostB
Router forwarding packet...
Message received at hostB
HostA sending packet 5 to HostB
Router forwarding packet...
Message received at hostB
```

> Note: Due to the 100ms propagation delay on each link, each packet arrives at HostB approximately 200ms after being sent (100ms HostA→Router + 100ms Router→HostB).

---

## File Descriptions

### `Network.ned`
Defines the entire network topology using OMNet++'s Network Description Language.
- Declares `Host` as a simple module with `isSource` and `hostName` parameters.
- Declares `Router` as a simple module with a 2-element gate array.
- Assembles the `Network` with `hostA`, `router`, and `hostB` as submodules.
- Connects `hostA ↔ router.port[0]` and `hostB ↔ router.port[1]` with **100ms delay**.

### `Host.h` / `Host.cc`
Implements a dual-role host:
- **Source role** (`isSource = true`): Schedules and sends 5 packets at 1-second intervals starting at t=1s.
- **Destination role** (`isSource = false`): Receives packets and prints `"Message received at hostB"`.

### `Router.h` / `Router.cc`
Implements stateless packet forwarding:
- Inspects the arrival gate index.
- Forwards to the opposite port (`port[0] → port[1]` or `port[1] → port[0]`).
- Prints `"Router forwarding packet..."` for every forwarded packet.

### `omnetpp.ini`
Configures the simulation:
- Sets the active network to `Network`.
- Limits simulation time to 20 seconds.
- Uses `cmdenv` (non-graphical) for terminal output.

---

## Simulation Parameters

| Parameter | Value |
|-----------|-------|
| Number of packets sent | 5 |
| Inter-packet interval | 1 second |
| Link delay (each hop) | 100 ms |
| Total end-to-end delay | ~200 ms |
| Simulation time limit | 20 seconds |

