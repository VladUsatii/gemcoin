# Core

A Pythonic interface to the blockchain.

## How does Core work?

Core combines three types of functions into an omniscient handler:

```
- Transactions
  * A way to send them
  * A way to program contracts
    * On chain interactions
    * Off chain interactions (e.g. scheduled transactions)

- Mining blocks
  * A way to guess nonce
  * Verification of block (block integrity)
  * A mechanism for sending block proposals to peers
    * Peer verification of blocks

- Data Updates
  * Performs requests for headers and blocks
  * Performs verifications of header/blocks and dumps any wrong transactions
```

The omniscient handler is:

```
- Omniscient Network Handler
  * Asynchronous collection of mempool transactions, block mining, and header/block updating (based on node level)
  * Default operation mode (./peers/main.py)
```

## Running Omniscient Handler

This system works differently than Ethereum, Bitcoin, and other cryptocurrencies. In Gemcoin's system, one single peer-to-peer network asynchronously connects to peers and requests data based on its current "need." A clock system refuses any malicious overflows of transaction/header broadcasts. A clock is useful for requesting blocks if a block update is assumed.

To run, use:

```
#tbd
```

## Sending a transaction 📧

To send a transaction, open up a new file. This is where you want to have stored your private key, public key, and address.

First, write out:

```python3
raw_tx = ConstructTransaction(...)
```

Then, make sure to construct a valid signature using the following function:

```python3
from sendShards import *

priv_key = "..." # must be in hex format
pub_key = "..." # must be in hex format

signed_tx = SignTransaction(raw_tx, priv_key)
```

To locally validate your transaction (like every other node will), run..

```python3
ConfirmTransactionValidity(signed_tx)

# if returns True : should be sent as a valid transaction (the signed_tx variable should be broadcast to peers)
# if returns False : should NOT be sent as a valid transaction and will be dumped by peers
```

To pack your transaction before sending, run..

```python3
tx_value = PackTransaction(signed_tx) # outputs in bytes(hex)
```

The above function created your "value" (read up on key-value stores before continuing).

To create your "key" for the database:

```
tx_key = CreateKey(signed_tx)
```

Add the transaction to your own mempool beore sending your mempool to other nodes:

```
cache = Cache('mempool')
cache.Create(tx_key, tx_value, cache.DB)
```

To send your transaction directly to another node, add this to your opcode handler (use 0x05 - Transaction with 0x00 data). The following will run when a node is connected and verified:

```python3
sendTransaction(signed_tx, src_node, dest_node, dhkey)
```

If you didn't do a direct message to another node, make sure that you run ```gemcoin/peers/main.py``` when you are ready.

It is that easy to be your own Gemcoin bank.

---

Created by Vlad Usatii @ youshould.readproduct.com.


NOTE: This is one of the most stress-inducing concepts I've ever written documentation on or programmed. I want everyone to know that with enough perseverance, anything can be programmed.. even if you don't have a high-school diploma.
