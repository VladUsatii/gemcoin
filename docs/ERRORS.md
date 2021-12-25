# Errors

## Overview

In Gemcoin Protocol, there are 128 error messages allocated and handled by the wire protocol.

## Meanings of every error

**IdleNodeError**

```
TcpServer.connect_with_node: Can't establish a communication with an idle node.
```

When (TCP) P2P Discovery can't successfully establish a connection with a node on the network (e.g. a host on a DNS seed or a local peer shut off its connection at the same moment you started yours), this error is thrown. It is ignorable. It simply resolves with ```continue``` in the for loop of searched nodes. It has no negative effect on the network and you aren't charged an electric fee for peer discovery.
