# Key Documentation

A public key and a private key are not transformable, but a private to public is (CHF).

## Generating a Private Key

```bash
>>> dubcoin cli

> create private key
> print private key
[ output ]
```

## Generating a Public Key

Public keys are derived from the private key. We currently use ECDSA (Elliptic Curve Digital Signature Algorithm) to sign transactions with a private key available only to the source IPv6 address of the transaction headers.

```bash
> get public key
> print public key
[ output ] 
```


