# Node Persistence Protocol v. 1

There are two types of messages that a peer-to-peer network of inbound and outbound nodes use. ```Checkup()``` persistently "pings" the destination host with useful data, and serves as a tap on the shoulder for TCP to continue its connection. As we all know, TCP closes a "hole" between hosts after a few seconds. On the contrary, the ```Disconnect()``` function pings the destination host and alerts them that they have a 10-second head start to attempt a disconnect before the src node disconnects. This helps nodes running on boomer computers have enough time to panic before an exception is thrown and both nodes are taken offline.

## Checkup 🔌

Checkup has a generic header:

```
0x00 || version_hash || protocol (e.g. PythonicGemcoin) || port || opcode || public_key
```

- 0x00 represents Checkup's list opcode.
- Version_hash is the git hash of each node. A connection persists if both hashes are the same. Otherwise, it assumes a fork or untrustworthy node.
- Protocol is the literal name of the program.
- Port is the TCP port that all connections to the blockchain are listening on.
- Opcode is the "subprotocol" layer.
- Public key is the src node's public key.

Checkup's "subprotocol layer" has a few opcodes:

```
0x00  |  Preserves connection between both nodes (math.ceil() syncs a connection to the nearest 10 seconds)
0x01  |  Warns destination host (node) that a huge "message" or string of packets is incoming and a database
      |  /storage must be initialized.
0x02  |  A level-2 based specification; has custom responses. This is currently not implemented or documented.
```

## Disconnect ❌

Disconnect has a generic header. It is way smaller than a Checkup, due to the untrustworthy connection caused by a Disconnect error. This prevents access to the chain from a faulty node. Irregardless, the header is:

```
0x01 || port || error
```

- 0x01 represents Disconnect's list opcode.
- Port represents the port of the communication, regardless of whether the nodes are on the same blockchain or not.
- Error is the literal error opcode.

The literal error opcodes are as follows:

```
0x00  |  manual disconnect
0x01  |  misbehaved node
0x02  |  useless node
0x03  |  incompatible peer
0x04  |  TCP crash
0x05  |  Man-in-the-middle attack introduced
0x06  |  Node connected to self
0x07  |  TCP timeout
0x08  |  layer 2 subprotocol request
```
