---
marp: true
footer: CS305 Computer Network Final Project

---

# Reliable Data Transfer and Congestion Control
11812102 Weijie HUANG, 11812104 Wenxuan SHI

---

# Design

- Full duplex RDT protocol
- Maintain multiple links simultaneously

---

# The Protocol: Full Duplex

When we need to **acknowledge** a packet and **send** a packet at the same time. Pack them together, don't waste the buffer size.

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

Hash function (散列算法), one-bit difference leads to huge difference in hash result.

We use MD5 (128bit), because it is very common and relatively fast.

---



---

# Implementation

High Performance Threading Model