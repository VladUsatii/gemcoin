# Peers

### Overview

Finding remote peers is quite challenging. There is a certain tradeoff between having a list of on-demand nodes and having decentralization from randomized broadcast for nodes. We've chosen the centralized tradeoff to increase the size of the network. Our reasoning is quite backed: if a seed discovers more nodes, they add those nodes to their publicNodeList, which is then saved to a seed.

## Finding Remote Peers

To find a remote peer, contact "gemcoin DNS servers" and the response section will contain a query of <25 outbound peers.

**Seeds**

```
dig seed.gemcoiners.com
```

We don't have many functioning seeds. If anybody has an interest in running a remote seed, submit a pull request and add in your server link with dig above.

## Finding Local Peers

Local peer discovery is done by traversing the list of usable IP addresses in a local network. Their public IPs are added to the list of static remote nodes.


