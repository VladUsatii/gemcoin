# Errors

## Overview

In Gemcoin Protocol, there are 128 error messages allocated and handled by the wire protocol.

### Help

```
(ErrorMessage) ?		: signifies that there are multiple reasons for this error and below are all documented reasons for the error.
TcpServer.function()	: signifies that a transport/network error has occurred. This error is a local issue.
```

## Meanings of every error

**IdleNodeError**

```
TcpServer.connect_with_node: Can't establish a communication with an idle node.
```

When (TCP) P2P Discovery can't successfully establish a connection with a node on the network (e.g. a host on a DNS seed or a local peer shut off its connection at the same moment you started yours), this error is thrown. It is ignorable. It simply resolves with ```continue``` in the for loop of searched nodes. It has no negative effect on the network and you aren't charged an electric fee for peer discovery.

**NodeIncompatibilityError**

```
(NodeIncompatibilityError) ?
```

All documented instances and meanings (?):

*Index doesn't exist on node. Node is on another chain/protocol.*

This error shows us that our node doesn't have an ID. This means that it is on a previous version of the network (pre-hash) or it doesn't exist on the current protocol. It simply has the same port and address as a common node.
