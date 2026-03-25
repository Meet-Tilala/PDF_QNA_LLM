# SUB - PUB Lab Assignment 3
## Meet Tilala -- B23CS1036

---

## System Overview

This implementation is a Publisher–Subscriber messaging system built with TCP sockets in C.
It consists of **6 programs** communicating over TCP using a Broker as the central hub.

```
  PUB1 ──────►┐                   ┌──────► SUB1 (sports, weather)
              │   BROKER (poll)   │
  PUB2 ──────►┘                   ├──────► SUB2 (technology)
                                  └──────► SUB3 (sports, technology)
```

---

## Components

| File        | Role                                        |
|-------------|---------------------------------------------|
| `broker.c`  | Central broker; routes messages via `poll()`|
| `pub1.c`    | Publisher 1 — topics: sports, weather       |
| `pub2.c`    | Publisher 2 — topic : technology            |
| `sub1.c`    | Subscriber 1 — subscribed: sports, weather  |
| `sub2.c`    | Subscriber 2 — subscribed: technology       |
| `sub3.c`    | Subscriber 3 — subscribed: sports, technology|

---

## Fixed Configuration

### Publisher Permissions & Messages
| Publisher | Topics Published     | Messages Sent                     |
|-----------|----------------------|-----------------------------------|
| PUB1      | sports, weather      | `vkohli` (sports), `rainy` (weather) |
| PUB2      | technology           | `cricket`                         |

### Subscription Mapping
| Subscriber | Subscribed Topics     | Receives                               |
|------------|-----------------------|----------------------------------------|
| SUB1       | sports, weather       | `sports:vkohli`, `weather:rainy`       |
| SUB2       | technology            | `technology:cricket`                   |
| SUB3       | sports, technology    | `sports:vkohli`, `technology:cricket`  |

### Timing (Strict Alternation Every 5 Seconds)
```
t =  0s : PUB1 sends  sports:vkohli  AND  weather:rainy
t =  5s : PUB2 sends  technology:cricket
t = 10s : PUB1 sends  sports:vkohli  AND  weather:rainy
t = 15s : PUB2 sends  technology:cricket
... (continues indefinitely)
```

---

## Message Format

### Publisher → Broker
```
PUBLISHER:topic:message\n
```
Examples:
```
PUB1:sports:vkohli
PUB1:weather:rainy
PUB2:technology:cricket
```

### Broker → Subscriber
```
topic:message\n
```
Examples:
```
sports:vkohli
weather:rainy
technology:cricket
```

### Identity Message (first message sent on connect)
```
PUB1\n   or   PUB2\n   or   SUB1\n   or   SUB2\n   or   SUB3\n
```

---

## How to Compile

### Option A — Using Makefile (recommended)
```bash
make
```
This builds: `broker`, `pub1`, `pub2`, `sub1`, `sub2`, `sub3`

To clean:
```bash
make clean
```

### Option B — Compile each file manually
```bash
gcc -Wall -Wextra -std=c11 -o broker broker.c
gcc -Wall -Wextra -std=c11 -o pub1   pub1.c
gcc -Wall -Wextra -std=c11 -o pub2   pub2.c
gcc -Wall -Wextra -std=c11 -o sub1   sub1.c
gcc -Wall -Wextra -std=c11 -o sub2   sub2.c
gcc -Wall -Wextra -std=c11 -o sub3   sub3.c
```

---

## How to Run

Open **6 separate terminal windows** (or use `tmux`/`screen`).  
**Start in this exact order:**

### Step 1 — Start the Broker (Terminal 1)
```bash
./broker
```
Expected output:
```
============================================
[Broker] Pub-Sub Broker started on port 8080
============================================
```

### Step 2 — Start Subscribers (Terminals 2, 3, 4)
```bash
./sub1     # Terminal 2
./sub2     # Terminal 3
./sub3     # Terminal 4
```

### Step 3 — Start Publishers (Terminals 5, 6)
Start both publishers roughly at the same time:
```bash
./pub1     # Terminal 5  (sends immediately, then every 10s)
./pub2     # Terminal 6  (waits 5s first, then every 10s)
```

> **Important:** Start both publishers close together (within a second) so the
> 5-second offset timing works as intended.

---

## Expected Output

### Broker
```
[Broker] Identified: PUB1  type=Publisher
[Broker] Identified: PUB2  type=Publisher
[Broker] Identified: SUB1  type=Subscriber
[Broker] Identified: SUB2  type=Subscriber
[Broker] Identified: SUB3  type=Subscriber
[Broker] Message from PUB1: PUB1:sports:vkohli
[Broker] Forwarded 'sports:vkohli' --> SUB1
[Broker] Forwarded 'sports:vkohli' --> SUB3
[Broker] Message from PUB1: PUB1:weather:rainy
[Broker] Forwarded 'weather:rainy' --> SUB1
[Broker] Message from PUB2: PUB2:technology:cricket
[Broker] Forwarded 'technology:cricket' --> SUB2
[Broker] Forwarded 'technology:cricket' --> SUB3
...
```

### SUB1 (sports + weather)
```
[SUB1] Received : sports:vkohli
[SUB1] Received : weather:rainy
```

### SUB2 (technology only)
```
[SUB2] Received : technology:cricket
```

### SUB3 (sports + technology)
```
[SUB3] Received : sports:vkohli
[SUB3] Received : technology:cricket
```

---

## Technical Design Notes

1. **`poll()` for concurrency** — The broker uses a single `poll()` loop over all
   file descriptors (listening socket + all client sockets). No threads are used.

2. **Line-buffered receive** — Each client has a dedicated accumulation buffer in
   the broker. Data is accumulated until a `\n` is found, ensuring correct parsing
   even if TCP delivers multiple messages in one `recv()` call.

3. **Persistent connections** — All clients connect once and keep their connection
   for the entire duration of execution.

4. **TCP_NODELAY on publishers** — PUB1 sets `TCP_NODELAY` to disable Nagle's
   algorithm, ensuring the two rapid sends (sports + weather) go out as separate
   TCP segments.

5. **Port** — All programs use `127.0.0.1:8080`. Change `BROKER_PORT` in each
   file to use a different port.

---

## Stopping the System

Press `Ctrl+C` in each terminal window to terminate the processes.

---

## File Summary

```
pubsub/
├── broker.c     ← Broker server (poll-based, routes messages)
├── pub1.c       ← Publisher 1  (sports + weather, sends every 10s)
├── pub2.c       ← Publisher 2  (technology, 5s offset then every 10s)
├── sub1.c       ← Subscriber 1 (sports + weather)
├── sub2.c       ← Subscriber 2 (technology)
├── sub3.c       ← Subscriber 3 (sports + technology)
└── README.md    ← This file
```
