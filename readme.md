#  Reliable Data Transfer — ARQ Protocols
### CN Lab 6 | B23CS1036


---

##  Table of Contents

1. [Overview](#overview)
2. [What is ARQ?](#what-is-arq)
3. [Q1 — Stop-and-Wait ARQ](#q1--stop-and-wait-arq)
4. [Q2 — Go-Back-N ARQ](#q2--go-back-n-arq)
5. [Q3 — Selective Repeat ARQ](#q3--selective-repeat-arq)
6. [How to Compile & Run](#how-to-compile--run)
7. [Protocol Comparison](#protocol-comparison)

---

## Overview

This lab implements three classic **Automatic Repeat reQuest (ARQ)** protocols that form the backbone of reliable data communication in real-world networks (TCP, Wi-Fi, Bluetooth, satellite links). Each protocol simulates:

-  Frame transmission with sequence numbers
-  Random packet/ACK loss using `rand()`
-  Retransmission logic specific to each protocol
-  Console output showing every transmission event

---

## What is ARQ?

When data travels across a network, packets can be **lost, corrupted, or delayed**. ARQ protocols handle this by:

1. The **sender** transmits a frame and starts a timer
2. The **receiver** sends back an **ACK** (acknowledgement) if the frame arrives correctly
3. If no ACK is received before the timer expires → the sender **retransmits**

Three generations of ARQ exist, each smarter than the last:

```
Generation 1 ──────► Stop-and-Wait      (send 1, wait, repeat)
Generation 2 ──────► Go-Back-N          (send window, on error rewind all)
Generation 3 ──────► Selective Repeat   (send window, on error retransmit only lost)
```

---

## Q1 — Stop-and-Wait ARQ

###  Concept

The simplest ARQ protocol. The sender transmits **exactly one frame**, then halts and waits for an ACK before moving on.

```
Sender                          Receiver
  │                                │
  │──── Frame 0 ──────────────────►│
  │                                │◄── processes frame
  │◄─── ACK 0 ─────────────────────│
  │                                │
  │──── Frame 1 ──────────────────►│
  │         ✗ ACK lost             │
  │                                │
  │──── Frame 1 (retry) ──────────►│  ← retransmit same frame
  │◄─── ACK 1 ─────────────────────│
  │                                │
```

###  Key Design Decisions

| Feature | Detail |
|---|---|
| Sequence numbers | Only **0 and 1** — alternating (1-bit sequence space) |
| Window size | Always **1** frame |
| Retransmit trigger | ACK not received (simulated as random loss) |
| Loss simulation | `rand() % 10 < 3` → ~30% loss chance |

###  Code Walkthrough

```cpp
// The entire protocol logic fits in one elegant loop:

int seqNum = 0;                         // Start with frame 0

for (int i = 0; i < totalFrames; i++) {
    bool ackReceived = false;

    while (!ackReceived) {              // Keep retrying until ACK arrives
        cout << "Sending Frame " << seqNum << endl;

        if (isACKReceived()) {          // Random simulation of ACK delivery
            cout << "ACK received for Frame " << seqNum << endl;
            ackReceived = true;
        } else {
            cout << "ACK lost! Retransmitting Frame " << seqNum << endl;
        }
    }

    seqNum = 1 - seqNum;               // Toggle: 0→1→0→1 (bit flip trick)
}
```

**The bit-flip trick** `seqNum = 1 - seqNum` elegantly alternates between 0 and 1 without any `if` statement.

**Why only 0 and 1?** Since only one frame is ever "in flight," you only need to distinguish the current frame from the previous one — 1 bit is sufficient.

###  Sample Output

```
Sending Frame 0
ACK received for Frame 0

Sending Frame 1
ACK lost! Retransmitting Frame 1

Sending Frame 1
ACK received for Frame 1

Sending Frame 0
ACK received for Frame 0

Transmission Completed
```

###  Limitation

Stop-and-Wait is **extremely inefficient** on high-latency links. If a network has 100ms round-trip time, the sender is idle for 100ms after every single frame — leading to very low channel utilization. This directly motivated the sliding window protocols below.

---

## Q2 — Go-Back-N ARQ

###  Concept

The sender maintains a **sliding window** of `N` frames and can transmit all of them without waiting for individual ACKs. But if *any* frame fails — **all frames from that point onward** are retransmitted.

```
Window Size = 4

Sender                              Receiver
  │                                    │
  │──── Frame 0 ──────────────────────►│ ✓ ACK 0
  │──── Frame 1 ──────────────────────►│ ✓ ACK 1
  │──── Frame 2 ──────────────────────►│ ✗ ERROR at Frame 2
  │──── Frame 3 ──────────────────────►│ ✗ discarded (2 not received yet)
  │                                    │
  │  ◄─── Go Back to Frame 2! ─────────│
  │                                    │
  │──── Frame 2 ──────────────────────►│ ✓ ACK 2
  │──── Frame 3 ──────────────────────►│ ✓ ACK 3
  │──── Frame 4 ──────────────────────►│ ✓ ACK 4
  │──── Frame 5 ──────────────────────►│ ✓ ACK 5
```

###  Key Design Decisions

| Feature | Detail |
|---|---|
| Window size | User-defined (e.g., 4) |
| Sequence numbers | `0` to `totalFrames - 1` |
| On error at frame `k` | Retransmit frames `k, k+1, ..., end of window` |
| Window advance | Only when ALL frames in the window are ACKed |

###  Code Walkthrough

```cpp
int base = 0;   // The leftmost unacknowledged frame (start of window)

while (base < totalFrames) {
    int end = min(base + windowSize, totalFrames);  // Right edge of window

    // ── TRANSMIT entire window at once ──
    cout << "Sending Frames:";
    for (int i = base; i < end; i++)
        cout << " " << i;

    // ── SIMULATE ACK reception, frame by frame ──
    int errorFrame = -1;
    for (int i = base; i < end; i++) {
        if (hasError()) {
            errorFrame = i;           // Mark where the error struck
            cout << "Error occurred at frame " << i << endl;
            break;                    // Stop processing further ACKs
        } else {
            cout << "ACK received for frame " << i << endl;
        }
    }

    // ── DECISION: slide forward or go back ──
    if (errorFrame != -1) {
        cout << "Retransmitting from frame " << errorFrame << endl;
        base = errorFrame;            // ← The "Go-Back" step
    } else {
        base = end;                   // All good — advance the window
    }
}
```

**Key insight:** `base = errorFrame` is the core of Go-Back-N. By resetting `base` to the error point, the next loop iteration automatically rebuilds a window starting from the failed frame — no extra bookkeeping needed.

###  Sample Output

```
Sending Frames: 0 1 2 3

ACK received for frame 0
ACK received for frame 1
Error occurred at frame 2

Retransmitting from frame 2

Sending Frames: 2 3 4 5

ACK received for frame 2
ACK received for frame 3
ACK received for frame 4
ACK received for frame 5
```

###  Limitation

Go-Back-N wastes bandwidth — if frame 2 fails in a window of 10, frames 3–9 (which arrived fine) are **thrown away** and retransmitted needlessly. Selective Repeat solves this.

---

## Q3 — Selective Repeat ARQ

###  Concept

The most sophisticated ARQ. The sender transmits a full window, but the receiver **buffers out-of-order frames** instead of discarding them. Only the **specific lost frame** is retransmitted — not the whole window.

```
Window Size = 4

Sender                              Receiver
  │                                    │
  │──── Frame 0 ──────────────────────►│ ✓ ACK 0  → delivered immediately
  │──── Frame 1 ──────────────────────►│ ✓ ACK 1  → delivered immediately
  │──── Frame 2 ──────────────────────►│ ✗ LOST   → (nobody home)
  │──── Frame 3 ──────────────────────►│ ✓ ACK 3  → buffered (2 is missing)
  │                                    │
  │    ◄── timeout for Frame 2 only ───│
  │                                    │
  │──── Frame 2 (retry) ──────────────►│ ✓ ACK 2  → delivered
  │                                    │           → Frame 3 flushed from buffer
```

###  Key Design Decisions

| Feature | Detail |
|---|---|
| Sender window | Tracks which frames are unacknowledged |
| Receiver window | Accepts and buffers frames **within** window range |
| `delivered[]` array | Tracks which frames have been in-order delivered |
| `buffered[]` array | Stores frames received out-of-order |
| Retransmit trigger | Per-frame timeout — **only the missing frame** |
| Buffer flush | After retransmitted frame arrives, deliver all consecutive buffered frames |

###  Code Walkthrough

```cpp
vector<bool> delivered(totalFrames, false);  // Has this frame been delivered in order?
vector<bool> buffered(totalFrames, false);   // Is this frame waiting in the buffer?
int base = 0;  // Next expected in-order frame

// On receiving frame i:
if (i == base) {
    //  In-order arrival: deliver immediately
    delivered[i] = true;
    cout << "Delivering Frame " << i << "\n";
    base++;

    //  THE KEY: cascade-deliver all consecutive buffered frames
    while (base < totalFrames && buffered[base]) {
        cout << "Delivering buffered Frame " << base << "\n";
        delivered[base] = true;
        base++;
    }
} else {
    //  Out-of-order: store in buffer, send ACK anyway
    buffered[i] = true;
    cout << "Frame " << i << " buffered\n";
}
```

**The cascade flush** (`while buffered[base]`) is the heart of Selective Repeat. When the missing piece finally arrives, it triggers a domino effect — all consecutive buffered frames are delivered instantly in order.

### Sample Output

```
Sender Window: 0 1 2 3
Sending Frame 0
Sending Frame 1
Sending Frame 2
Sending Frame 3

Receiver:
Frame 0 received correctly
ACK 0 sent
Delivering Frame 0

Frame 1 received correctly
ACK 1 sent
Delivering Frame 1

Frame 2 lost during transmission

Frame 3 received (out of order)
ACK 3 sent
Frame 3 buffered

Sender timeout for Frame 2
Retransmitting Frame 2

Receiver:
Frame 2 received correctly
ACK 2 sent
Delivering Frame 2
Delivering buffered Frame 3
```

---

## How to Compile & Run

### Prerequisites

| Platform | Requirement |
|---|---|
| Linux / macOS | `g++` (usually pre-installed) |
| Windows | Install [MinGW](https://www.mingw-w.org/) **or** use an IDE like Code::Blocks / Dev-C++ |

### Step 1 — Compile

```bash
g++ q1_stop_and_wait.cpp  -o q1
g++ q2_go_back_n.cpp      -o q2
g++ q3_selective_repeat.cpp -o q3
```

### Step 2 — Run

**Q1 — Stop-and-Wait:**
```bash
./q1
# Enter number of frames to send: 4
```

**Q2 — Go-Back-N:**
```bash
./q2
# Enter total number of frames: 6
# Enter window size: 4
```

**Q3 — Selective Repeat:**
```bash
./q3
# Enter total number of frames: 4
# Enter window size: 4
```

> **Windows users:** replace `./q1` with `q1.exe`, etc.

###  Notes

- Output is **non-deterministic** by design — each run uses `srand(time(0))` to seed random loss. Run multiple times to observe both successful transmissions and retransmissions.
- To get a **fixed/reproducible** output for testing, replace `srand(time(0))` with `srand(42)` (or any constant seed).

---

## Protocol Comparison

| Feature | Stop-and-Wait | Go-Back-N | Selective Repeat |
|---|:---:|:---:|:---:|
| Frames in flight at once | 1 | N (window) | N (window) |
| Sequence number bits needed | 1 | ≥ log₂(N+1) | ≥ log₂(2N) |
| On frame error, retransmit | 1 frame | All from error onward | Only the lost frame |
| Receiver buffer required | No | No | Yes |
| Bandwidth efficiency | 1/5 | 3/5 | 5/5 |
| Implementation complexity | Simple | Moderate | Complex |
| Real-world example | Basic modems | Older TCP | Modern TCP / Wi-Fi |

### Efficiency Formula

The **channel utilization** (fraction of time the sender is actually sending) is:

```
Stop-and-Wait:   U = 1 / (1 + 2a)          where a = propagation delay / transmission time
Go-Back-N:       U = N / (1 + 2a)           if N ≥ 1 + 2a, else same as Stop-and-Wait
Selective Repeat: U = N / (1 + 2a)          same formula but wastes no retransmissions
```

For a satellite link where `a = 50` (very high latency), Stop-and-Wait utilization drops to ~1%. Go-Back-N and Selective Repeat with large windows recover most of that lost throughput.

---

*Lab 6 — Computer Networks | ARQ Protocol Simulation in C++*
