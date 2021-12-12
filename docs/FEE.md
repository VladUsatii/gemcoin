# Fee Breakdown

A fee in cryptocurrency (especially general-purpose chains) allows users only *n* computational resources, based on a fee paid through the exchange itself. This devalues the coin, while limiting the transact allotted to machines. To reduce the cost of transactions and allow users to keep their coins, an "electric" fee mechanism is proposed. This would persistently increase coin supply while decreasing transaction traffic on the chain.

## Electric Fee: A General Overview

In order to stifle transactions and create a slow, yet accessible chain, a fee is created. Our fee comes in the form of computational resources expended on the source machine.

Here are some definitions:

```
time					: time is specifically defined as given guess time divided by complete hashes in block s. A new block creates a new instance of appending the first average to the next average and so on.
C(x) -> uint64			: C(x) marks the measured mining time of input machine x. This is the time spent by user x on the mainnet, verifying transactions and mining blocks. Mining time is measured in complete guessed hashes per given time period and bonuses are awarded to successful verifications and creations of blocks.
V(x) -> uint32			: input C(x) to the arbitrary function V converts mining time to transact time.
```

Let us say that user A spent 10 minutes with a specialized ASIC chip (arbitrary, identified asset) on the mainnet. Total, it took him 605 seconds to guess 6 hashes. Then, a new block appears. The user continues to mine and creates a new average. In this process, user A generated mining time, stored as a number. The user in this process then converted some of his compute time to electricity via function ```C(x)```.

Now, let us say that user A wants to send 0.001 or 10^-3 gems to user B. This user does not want to spend valuable mined coins on a transaction that may or may not have been hardcoded through a contract. In order to send this transaction and keep the ledger free of fees, a function ```V(x)``` takes in mining time ```C(x)``` and converts one-way to transaction time V(x). Transaction time is the designated time that a blockchain function can be carried out.

When time has run out of user A's V(x) storage, UDP will drop all packets. Dropped packets will alert user B that there is not enough compute time to convert to transact time, therefore only a fraction of the recorded currency will be transacted.
