# Block Header Specification

Every block, when stored, is __ bytes.

## Structure

A constructed block header looks like the following:



A deconstructed block header dictionary is structured in the following:

```
{
"version"      : version       uint32_t 4 bytes,
"previous_hash": previous_hash char[32 bytes],
"mix_hash"     : mix_hash      char[32 bytes],
"timestamp"    : timestamp     uint32_t 4 bytes,
"targetEncoded": targetEncoded uint32_t 4 bytes,
"nonce"        : nonce         uint32_t 4 bytes,
"num"          : num           uint32_t 4 bytes,
"txHash"       : txHash        char[32 bytes],
"uncleRoot"    : uncleRoot     char[32 bytes]
}
```
