# December 2021

**By Vlad Usatii**

December has seen a lot of changes. In fact, December was my first month of pushing updates to the python gemcoin protocol.

The initial creation of my project ended up being quite harder than expected. In fact, I like to summarize the difficulty of building a blockchain with the following pseudo-graph. You are told what is important, but you aren't told how much accidental complexity arises when you implement the important things:

![Accidental complexity and essential complexity graph](https://www.simplethread.com/wp-content/uploads/2020/10/Ess-vs-Acc.png)

It all started with the first write of my code. I was making a peer discovery protocol for local nodes. It ended up being a mess. I had no idea how socket worked, even in something as trivial as Python (should be trivial to me at this point). To make up for my lack of understanding, I wrote a client-to-server and client-server-client model using both TCP and UDP, left it in a reference folder, and built a peer-to-peer (client-to-client) model using functional notation. After mastering the art of building P2P in Python, I decided to add error handling, callbacks, the ability to add more than one functional node, and so forth. This led me to building out a class for the Node and Nodeconnection.

I ended up going too far. I started working on the verification of the peer's header and git hash. I added AES encryption of packets on the transport layer and added a bit of CMD for the application layer. I started working with ecdsa (elliptic curve digital signature algo), sha, and private WIF -> public -> sig and multisig. I didn't get very far in any of these efforts, but I successfully built a functional and programmable network with dev tools.

TODO:

- Resolve the saving of peers on a localnode.txt file.
- Build out the structure of the blockchain.
- Build out the structure of AES encryption (headers, etc.).
- Improve security in general (I don't want to use git hashes because they can be modified before execution and could run exploitative code.

- Work on a wallet format.
- Build out CMD for basic commands.
- See my first validation of a block.
- See the first attempt at an initial block download through nginx or some lightweight key-value store.
