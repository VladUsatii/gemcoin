# Wire Protocol (v. 1)

User transition states use the following representations as symbols:

```
||:					concatenation
(x | y):			trunk notation signifies OR operator
src:				source device
dest:				destination device
node -> n:			a device returning its state on the network n
udp:				user datagram protocol returns unverified buffers over a port. This "unsafe" protocol is considered low-latency.
dhke(x) -> n:		diffie-hellman key exchange returns the secret number for transport protocol encryption and decryption
ecdsa(x) -> bytes:	returns ecdsa signature of a private key in bytes
sha256(x) -> y:		returns sha256-keccak hash on the input x
```

### Port Design:

I've designated port 1513 as the mainnet, allowing all communications concerning finding local nodes and updating user state to be transacted through this port. Test ports are ignored for this representation (testnets). The port is opened upon running the mainnet.

To scan the port for possible nodes on the network, pings are first run on the local network. If no devices are found listening on the port (no pong response), the ```findLocalNodes()``` function switches to a ```findRemoteNodes()``` function. Finding local nodes requires the use of nmap port scans. Finding remote nodes is a very difficult problem, on the other hand. Our solution involves DNS seeders. These expose a list of reliable nodes via a built-in DNS server on the network end-devices. This reduces electric fees significantly.

### Discovery Header Design

All discovery packets are symmetrically encrypted and authenticated in order to avoid static identification by firewalls.

```
packet			= initvector || masked-header || message
initvector		= random uint128 # for random data obfuscation
masked-header	= aes(dhke(x), initvector, header)
masked-key		= dest-name # dest-id[:16]
```

#### Ping/Pong Design

UDP shuffles a minimum of 63 bytes of a discovery header to local nodes or remote nodes after searching the local network. The ping response list is as follows:

```
Y(x) -> y:	YES response from input bytes x returns an IP address
N(x) -> y:	NO response from input bytes x returns None type
Z(x) -> y:	Z tag from input bytes x returns ErrorCode 0x01 (ValueError)
```

UDP shuffles back 32 bytes of an empty header to the source local node after a Y(None) connection is established. This verifies the existence of a gemcoin node.

### Key exchange:

A key exchange is necessary for the safe transmission and updateability of trusted nodes. To ensure a node is using the correct software, a Diffie-Hellman key exchange is necessary.

#### Key design

All ```dhke(x)``` functions are concatenated in the following layout before being sent:

```
"gemcoin-key-round-one" || exchange_one || "_" || host_rand_num
```

```"gemcoin-key-round-one"``` is a string representation of what key value you are sending. ```exchange_one``` is the output of the first key function, which is necessary to send to the destination. It will be used in round two for the creation of a unique key. ```"_"``` separates keys. ```host_rand_num``` is the random number input that was used for the first exchange output.

The function ping pongs simultaneously:

```
dhke(src) generates unique message z1
message is sent to dest
dhke(dest) generates unique message z2
message is sent to src
```

Both work with each other's public code:

```
dhke(z1) = dhke(z2)
dhke(z1 | z2) is the secret key
```

The key is used for AES encryption.

### Private Wiring

A key in a session allows for the verification of a node.

**Available in future update.**




