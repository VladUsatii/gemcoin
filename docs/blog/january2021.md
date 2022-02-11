# January 2022

This month has been a crazy ride.

What I've learned (hopefully in order):
- How to structure a header
	* What a header actually means
	* What the pros and cons of expanding a header size are, and what it means for the blocks and chainstate
- How to construct a block from the deconstructed header and a mempool of needy transactions
	* Why a smaller block size is better for productivity (maximized transactions/second)
	* Why a mempool sorted by highest "work" done on it is very important for the ongoing block generation from PoW
		* Sorting from High -> Low == maximize block reward
		* The problems of MEV (or BPEV) (Miner Extractable Value) and what it means for miners
			* Monopolies, hoarding money, miners make more than everyone else, etc.
- How to properly design two types of Proof of Work
	* Proof of work done by brute force via a target difficulty
		* can be exploited
	* Proof of work can be done through a memory-hard approach
		* DAGger uses Directed Acyclic Graphs to make a cache and dataset, which creates ASIC-resistance (democratizes mining)
- How to construct a transaction list (and merkle tree, recursive merkle hash, dhash)
- Game theoretic principles that are important in crypto-heterodox economics
	* Context-neutrality
	* Cost-benefit analyses
	* The cost of attacking 51% of a chain
- How to access a generic class with a LevelDB initializer for different instances of caches
	* I had so many errors based on the LOCK files not deleting
		* Fixed it with a generic class design

This month was the most progressive, ever-changing month that pushed me in many different ways.

Next month, I hope to wrap up the Cache-verification system and chainstate validation (among many peers) system that would allow 25-100 nodes to simultaneously connect and validate the chains.
	* Chains with the most work done will win over the chains with no work done.
		* Nodes always look for bigger chains.

February will also be the most important month in terms of designing the general-purpose aspect (custom functions and bytecode that is executed by miners). This is arguably the most difficult aspect of a general-purpose chain.

In addition, I've also documented how Electricity Fees work (the more work a transaction has done, the more prioritized the transaction is). This invisible fee would stabilize the network while eliminating taxes.
