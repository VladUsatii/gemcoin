
This is not a working project at the moment. When a full release is pushed, this tab will be removed.

----


# 💎💎💎

A Turing-complete, general-purpose blockchain. Gas fees are dumb, so we switched to electric.

| Current proposal				|
| ----------------------------- |
| Layer 1 mainnets and testnets |
| Lightning Networks			|
| Turing-completeness			|
| General-purpose computation	|
| Hidden gas fees (electric)	|
| Layer 2 support				|

## How it works 🌐

A general-purpose blockchain is a chain of digital signatures that avoid mediation of disputes and equate computational power over the network of peer-to-peer machines. This allows anyone to create decentralized applications for the peer-to-peer chain, accessible on the internet without centralized authority. In order to lower gas fees used for application computations, I devised a compute-based payment scheme.

### Premise

Gas fees are too expensive and are the reason that many dApps cease to exist. Cutting these fees would create instability in network usage regulations and become a major handicap for the network. To enforce a strict fee environment, an electricity-based fee must be incorported into the mainnet.

**Read the logic behind electric** [Fee Breakdown](https://github.com/VladUsatii/gemcoin/blob/main/docs/FEE.md)

## Current Ports

| Port Number	| Port Type	|
| ------------- | --------- |
| 1513			| Mainnet	|
| 1514			| Testnet 1	|
| 1515			| Testnet 2	|
| 1516			| Testnet 3	|

## Config ⚙️

To join the peer-to-peer server:

```bash
>>> git clone 'https://www.github.com/VladUsatii/gemcoin'
>>> cd gemcoin
>>> bash setup.sh
```

To listen on a gem network:

```bash
>>> gem [ net port number ]
Listening on [ net type (e.g. mainnet) ] . . .
```

## Versions

[GIP 1](https://github.com/VladUsatii/gemcoin/docs/GIP1.md)

## CLI

To develop on the blockchain, use our CMD tool and port to a language of your choice.

Ported languages so far are listed here:

*None*

## TODO

Set up a block format and private keygen.

---

Created by Vlad Usatii @ youshould.readproduct.com
