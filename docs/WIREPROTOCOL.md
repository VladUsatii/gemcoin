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

To scan the port for possible nodes on the network, pings are first run on the local network. If no devices are found listening on the port (localNode iterator returns False), the ```findLocalNodes()``` function switches to a ```findRemoteNodes()``` function. Finding local nodes requires the use of iterating the arp table. Finding remote nodes is a very difficult problem, on the other hand. Our solution involves DNS seeders. These expose a list of reliable nodes via a built-in DNS server on the network end-devices. This reduces electric fees significantly.

### Key exchange

A key exchange is necessary for the safe transmission and updateability of trusted nodes. To ensure a node is using the correct software, a Diffie-Hellman key exchange is necessary.

#### ID Design

Every node ID has (GIP 0) 3 indices:

```
[dhke(x): dest_dhke_one, x: host_rand_num, VERSION: hash]
```

Let's break the indices down:

**dhke(x)**:

```
dhke(host_rand_num) generates unique message z1
message is sent to dest
dhke(host_rand_num) generates unique message z2
message is sent to src
```

The initial ```dhke(x)``` is sent over a public channel. That is, it doesn't use AES because this is the node's initial interaction.

```
dhke(z1) = dhke(z2)
dhke(z1 | z2) is the secret key
```

The key is used for AES encryption.

**x**

The host's random number is generated per session and is a ```random.random x 100```.

**VERSION --> VERACK**

A VERSION message is sent over the public channel. If the node can't match the VERSION to it's host VERSION, the connection is cut. VERACK is returned False. If the version acknowledgement is successful, the VERACK returns True and the connection moves to verification of blocks.

### Request Header Design

All discovery packets are symmetrically encrypted and authenticated in order to avoid static identification by firewalls.

```
packet			= initvector || masked-header || message
initvector		= random uint128 # for random data obfuscation
masked-header	= aes(dhke(x), initvector, header)
masked-key		= dest-name # dest-id[:16]
```

The header is defined as the following:

```
unknown at the moment, in RD
```
