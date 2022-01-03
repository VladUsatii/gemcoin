# Errors

## Overview

In Gemcoin Protocol, there are 128 error messages allocated and handled by the wire protocol.

We also coined the term "detection flags," or crucial codes that show the current operation of the system. These are explained below first before moving on.

## Detection Flags 🚩

Detection flags are really important. They display the current state of your local system on the chain.

```
(yellow) VERSION: This flag shows the current version number. It can be seen by turning on MASTER debug in the code.

(green) INFO: The INFO flag shows a basic operation or continuation of the protocol.

(blue) SUCCESS: The SUCCESS flag shows a successful connection to a node. This is not to be confused with ACCOMPLISHED.

(blue) VALIDATED: The VALIDATED flag shows a successful validation of a transaction or a successful block spawn.

(blue) ACCOMPLISHED: This flag shows a successful transaction. It may also represent a successful data send (e.g. Initial Block Download).

(yellow) WARNING: This flag is activated on Ctrl+C. It warns the chain that you want to shut down the node.

(red) PANIC: This flag is a final-warning ctrl+C message. It can represent the interruption of a large task or a simple 10-warning shutdown from the open caches.
```

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
