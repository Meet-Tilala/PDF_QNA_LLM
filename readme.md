#  CN Lab 1 — Socket Programming
B23CS1036 - Meet Tilala

---

## Table of Contents

1. [Overview](#overview)
2. [Concepts](#concepts)
3. [Question 1 — One-to-One Chat](#question-1--one-to-one-chat-application)
4. [Question 2 — Group Chat](#question-2--multi-client-group-chat-application)
5. [How to Run](#how-to-run)
6. [Architecture Diagrams](#architecture-diagrams)
7. [Code Walkthrough](#code-walkthrough)
8. [Common Errors & Fixes](#common-errors--fixes)

---

## Overview

This lab implements two **real-time terminal chat applications** using Python's `socket` library — the same low-level building block that powers every web browser, messaging app, and server on the planet.

| | Q1 — One-to-One Chat | Q2 — Group Chat |
|---|---|---|
| **Type** | Peer-to-peer (1 server ↔ 1 client) | Multi-client (1 server ↔ N clients) |
| **Protocol** | TCP (`SOCK_STREAM`) | TCP (`SOCK_STREAM`) |
| **Concurrency** | 2 threads per side | 1 thread per client (server-side) |
| **Port** | `5000` | `6000` |
| **Termination** | `exit` / `quit` | `exit` / `quit` |


---

## Concepts

###  What is a Socket?

A **socket** is an endpoint for two-way communication between two programs over a network. Think of it as a **telephone** — one side calls (client), the other picks up (server), and they talk.

```
Client Socket  ←——— TCP Connection ———→  Server Socket
  (connects)                               (listens & accepts)
```

Python exposes this via the `socket` module:

```python
import socket
s = socket.socket(socket.AF_INET,   # Address Family: IPv4
                  socket.SOCK_STREAM) # Type: TCP (reliable, ordered)
```

###  The TCP Socket Lifecycle

```
SERVER                          CLIENT
  │                               │
  │  socket()                     │  socket()
  │  bind(host, port)             │
  │  listen()                     │
  │  accept()  ←────────────────  │  connect(host, port)
  │     │                         │     │
  │   recv() ←─────────────────── │   send()
  │   send() ──────────────────→  │   recv()
  │     │                         │     │
  │  close()                      │  close()
```

###  Why Threading?

Without threading, a process can only do **one thing at a time**. If your chat app is waiting to receive a message, it can't send one simultaneously. Threading solves this by running **send** and **receive** in parallel:

```
Main Thread  ──→  reads your keyboard input → sends to peer
Recv Thread  ──→  listens on socket          → prints incoming messages
```

---

## Question 1 — One-to-One Chat Application

###  Files

```
Q1_chat/
├── server.py   ← Run this first
└── client.py   ← Run this second
```

###  Goal

Two terminals. One server. One client. Both can talk to each other in real time.

```
┌─────────────────────┐         ┌─────────────────────┐
│     Terminal 1      │         │     Terminal 2      │
│   (server.py)       │◄───────►│   (client.py)       │
│                     │  TCP    │                     │
│  Server: Hello!     │         │  Client: Hi there!  │
│  Client: How are u? │         │  Server: Doing well │
└─────────────────────┘         └─────────────────────┘
```

---

## Question 2 — Multi-Client Group Chat Application

###  Files

```
Q2_group_chat/
├── server.py   ← Run this first (once)
└── client.py   ← Run this for each user (multiple terminals)
```

###  Goal

One central server that acts as a **message hub** — any message from one client is broadcast to all other connected clients.

```
          ┌────────────┐
          │   Server   │
          │  (hub)     │
          └─────┬──────┘
       ┌────────┼────────┐
       ▼        ▼        ▼
   [Alice]   [Bob]   [Charlie]
```

When Alice types `"Hello everyone!"` → Server receives it → Broadcasts `"Alice: Hello everyone!"` to Bob and Charlie.

---

## How to Run

### Prerequisites

- Python 3.6 or higher
- Two (or more) terminal windows
- No additional packages needed

###  Running Question 1 (One-to-One Chat)

**Step 1 — Start the server** (Terminal 1):
```bash
cd Q1_chat
python server.py
```
Expected output:
```
[Server] Listening on 127.0.0.1:5000 ...
```

**Step 2 — Connect the client** (Terminal 2):
```bash
cd Q1_chat
python client.py
```
Output:
```
[Client] Connected to server at 127.0.0.1:5000
[Client] Type 'exit' or 'quit' to end the chat.
```

**Step 3 — Chat!**
```
# Terminal 1 (Server)          # Terminal 2 (Client)
> Hey, are you there?           Client: Hey, are you there?
Server: Yes! Loud and clear.  > Yes! Loud and clear.
> exit                          [Server] Chat ended.
```

**To end the chat:** type `exit` or `quit` on either side.

---

###  Running Question 2 (Group Chat)

**Step 1 — Start the server** (Terminal 1):
```bash
cd Q2_group_chat
python server.py
```
Output:
```
[Server] Group chat server running on 127.0.0.1:6000
[Server] Waiting for clients...
```

**Step 2 — Connect Client 1** (Terminal 2):
```bash
python client.py
# Enter username: Alice
```

**Step 3 — Connect Client 2** (Terminal 3):
```bash
python client.py
# Enter username: Bob
```

**Step 4 — Connect Client 3** (Terminal 4):
```bash
python client.py
# Enter username: Charlie
```

**Step 5 — Chat!**

Alice's terminal:
```
Enter your username: Alice
[Client] Joined as 'Alice'. Type 'exit' to leave.

[Server] Bob has joined the chat.
[Server] Charlie has joined the chat.
Bob: Hey everyone!
> Hello Bob!
Charlie: This is so cool
```

**To leave:** type `exit` or `quit`.

---

## Architecture Diagrams

### Q1 — Threading Model

```
server.py Process
┌─────────────────────────────────────┐
│                                     │
│  Main Thread                        │
│  ┌──────────────────────────────┐   │
│  │  input() → send to client    │   │
│  └──────────────────────────────┘   │
│                                     │
│  Recv Thread (daemon)               │
│  ┌──────────────────────────────┐   │
│  │  recv() → print "Client: …"  │   │
│  └──────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
           (same structure for client.py)
```

### Q2 — Server Thread Pool

```
server.py Process
┌──────────────────────────────────────────────┐
│                                              │
│  Main Thread — accepts new connections       │
│  ┌─────────┐                                 │
│  │ accept()│──► spawns new thread per client │
│  └─────────┘                                 │
│                                              │
│  Thread for Alice   Thread for Bob   ...     │
│  ┌─────────────┐   ┌─────────────┐           │
│  │ recv()      │   │ recv()      │           │
│  │ broadcast() │   │ broadcast() │           │
│  └─────────────┘   └─────────────┘           │
│                                              │
│  Shared State: clients = { sock: username }  │
│  Protected by: threading.Lock()              │
└──────────────────────────────────────────────┘
```

---

## Code Walkthrough

### Q1 — `server.py` Explained

```python
# 1. Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. SO_REUSEADDR lets you restart the server without waiting for OS timeout
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 3. Bind to address — "claim this IP:port"
server_socket.bind((HOST, PORT))

# 4. Start listening — OS will queue up to 1 pending connection
server_socket.listen(1)

# 5. Block until a client connects — returns a NEW socket for that client
conn, addr = server_socket.accept()
```

> **Key insight:** `accept()` returns a *new* socket (`conn`) dedicated to this client.  
> The original `server_socket` keeps listening for future connections.

```python
# 6. Launch a background thread to receive messages concurrently
recv_thread = threading.Thread(target=receive_messages, args=(conn,), daemon=True)
recv_thread.start()

# 7. Main thread sends messages (reads from keyboard)
while True:
    message = input()
    conn.send(message.encode('utf-8'))  # Must encode str → bytes
```

> **Why `daemon=True`?** Daemon threads die automatically when the main thread exits,  
> preventing the program from hanging if the main loop ends.

---

### Q2 — `server.py` Explained

```python
# Shared data structure: maps each socket to its username
clients = {}

# A Lock prevents two threads from modifying `clients` simultaneously
# (Race condition: two clients disconnect at the exact same moment)
clients_lock = threading.Lock()
```

```python
def broadcast(message, exclude=None):
    # Send to ALL clients, except the sender themselves
    with clients_lock:              # Acquire lock — thread-safe access
        for client_sock in list(clients):   # list() creates a snapshot copy
            if client_sock == exclude:
                continue
            try:
                client_sock.send(message.encode('utf-8'))
            except Exception:
                # Dead connection — clean it up
                client_sock.close()
                del clients[client_sock]
```

```python
def handle_client(conn, addr):
    # First recv is always the username (protocol agreement between server & client)
    username = conn.recv(1024).decode('utf-8').strip()

    with clients_lock:
        clients[conn] = username            # Register this client

    broadcast(f"{username} has joined.", exclude=conn)

    while True:
        message = conn.recv(1024).decode('utf-8')
        if not message or message.lower() in ('exit', 'quit'):
            break                           # Graceful exit
        broadcast(f"{username}: {message}", exclude=conn)

    # Cleanup in finally — runs even if an exception occurs
    with clients_lock:
        del clients[conn]
    conn.close()
    broadcast(f"{username} has left the chat.")
```

> **Why `list(clients)` in broadcast?**  
> If a client disconnects while we iterate over `clients`, the dictionary  
> size changes mid-loop — causing a `RuntimeError`. Converting to a list  
> first creates a safe snapshot of keys at that moment.

---

### Q2 — `client.py` Explained

```python
# Username is sent as the very first message — the server expects this
username = input("Enter your username: ").strip()
client_socket.send(username.encode('utf-8'))

# Separate thread handles incoming group messages (non-blocking)
recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
recv_thread.start()

# Main thread handles what YOU type
while True:
    message = input()
    client_socket.send(message.encode('utf-8'))
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `Address already in use` | Previous server process still running | Wait 30s, or kill the old process: `lsof -ti:5000 \| xargs kill` |
| `Connection refused` | Server not running yet | Start `server.py` before `client.py` |
| `UnicodeDecodeError` | Binary data received instead of text | Ensure both sides use `.encode('utf-8')` / `.decode('utf-8')` |
| Messages appear jumbled | `input()` prompt mixed with received text | Known terminal limitation — messages are still delivered correctly |
| Server thread hangs on exit | Non-daemon threads blocking shutdown | All recv threads use `daemon=True` — this is already handled |

---

## Key Takeaways

- **`socket.socket(AF_INET, SOCK_STREAM)`** creates a TCP socket — reliable, ordered delivery
- **`bind()` + `listen()` + `accept()`** is the server's handshake sequence
- **`connect()`** is the client's handshake
- **`send()` / `recv()`** work on `bytes`, not strings — always encode/decode
- **Threading** enables simultaneous send + receive (full-duplex communication)
- **`threading.Lock()`** protects shared data from concurrent modification
- **`SO_REUSEADDR`** prevents "Address already in use" on server restart
- **`daemon=True`** ensures background threads don't prevent clean program exit

---

*Lab 1 — Computer Networks | Python Socket Programming*
