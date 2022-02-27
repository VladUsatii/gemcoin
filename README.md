
This is not a working project at the moment. When a full release is pushed, this tab will be removed.

----

![gemcoin logo](https://github.com/vladusatii/gemcoin/blob/main/gemcoin_logo.png?raw=true)

A Turing-complete, general-purpose blockchain. Gas fees are dumb, so we switched to electric.

**In newbie terms** : A hive-mind computer, where every computer, as long as it does the work, can participate in making decisions for the network. Each computer in the hive-mind can make apps that every computer can now hold for free.

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

| Port Number	| Port Type	| Magic Number |
| ------------- | --------- | ------------ |
| 1513			| Mainnet	| 0x3039       |
| 1514			| Testnet 1	| 0x12fd1      |
| 1515			| Testnet 2	| 0x15b38      |
| 1516			| Testnet 3	| 0x1869f      |

**Mainnet** --> A mainnet is the biggest hive-mind of computers.
**Testnets** --> A testnet is a local test of the hive-mind for applications. The test-net clears up every day to allow experimentation without consequence.

**Magic number** --> To connect to a "net" (a group of consenting nodes), you need to know which network is being initiated. A magic number specifies which group of nodes you are accepting.

## Config ⚙️

To join the peer-to-peer server:

```bash
>>> git clone 'https://www.github.com/VladUsatii/gemcoin'
>>> cd gemcoin
>>> # bash setup.sh # in production
>>> chmod +x main.py
>>> ./main.py # right now, this is what you run
```

To make a private key and submit it to the chain:

```bash
>>> python3 add_key.py [ priv_key ] # the key can be generated in the 'wallet' folder
```

## Versions

[GIP 1](https://github.com/VladUsatii/gemcoin/docs/GIP1.md)

## CLI

To develop on the blockchain, use our CMD tool and port to a language of your choice.

Ported languages so far are listed here:

*None*

## TODO

Debug and audit my code
Add some new classes to peek at the blocks from Library/Gemcoin folder

---

Created by Vlad Usatii @ youshould.readproduct.com
