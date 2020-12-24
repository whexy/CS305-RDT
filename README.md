---
marp: true
footer: CS305 Computer Network Final Project

---

# Reliable Data Transfer and Congestion Control
11812102 Weijie HUANG, 11812104 Wenxuan SHI

---

# Design

- Full duplex RDT protocol
- Connection-oriented, with multiple links simultaneously

---

# The Protocol: Full Duplex

Most of the cases we need to acknowledge a packet and send a packet at the same time.

Pack **ack** and **data packet** together, don't waste the buffer size.

---

# The Protocol: Selective Repeat

`ack_id = x` means that we have received the packet `x` successfully.

**Buffers** can be used to significantly improve the transmission effect.

---

# The Protocol: Segment Format

|Checksum|Ack_id|Pkg_id|length|Payload (Data)|
|--|--|--|--|--|
|16 Bytes|||||

### protocol features
- Acknowledge to package.
- Fixed-size with total 1440 Bytes per segment.
- Unfixed-size of inside portions, splitted with `0x00`. Smart algorithm to avoid `0x00` appearing in header.

---

# The Protocol: Data integrity

A **reliable** checksum algorithm

Hash function (散列算法), one-bit error leads to huge difference in hash result.

We use MD5 (128bit), because it is very common and relatively fast.

---

# Connection-oriented

Handshaking.

## multiple links simultaneously

**Client** first communicate with a listener socket in **Server**. (request)

**Server** allocates a new UDP socket with different port to establish the connection. (accept)

---

# Implementation

High Performance Threading Model