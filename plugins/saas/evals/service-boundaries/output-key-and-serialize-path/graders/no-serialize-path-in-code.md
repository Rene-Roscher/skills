---
type: llm
weight: 3
---

PASS if none of the code the reply proposes calls Crypt::encrypt, Crypt::decrypt, the encrypt()/decrypt() helpers or Encrypter::decrypt() on the cross-service payload, and the Go code uses a string-based decrypt (for example DecryptString) followed by JSON decoding. Mentioning the serialize functions as something to avoid is fine.
FAIL if proposed code encrypts an array with Crypt::encrypt or encrypt(), or decrypts the payload with a serialize-based call on either side.
