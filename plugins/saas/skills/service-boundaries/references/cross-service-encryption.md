# Cross-service encryption

## Contents
- Keys
- Laravel side
- Go, Node and Rust side
- Payload shape and receiver checks
- Rotation and failure
- Interop tests

Sources: Laravel `Encrypter`, https://github.com/laravel/framework/blob/12.x/src/Illuminate/Encryption/Encrypter.php;
https://github.com/Rene-Roscher/laravel-go-encryption, https://github.com/Rene-Roscher/laravel-node-encryption,
https://github.com/Rene-Roscher/laravel-rust-encryption (all verified 2026-10). Check the API of the installed
package version before copying a call.

## Keys

- One key per relationship, named after it: `CONNECTOR_ENCRYPTION_KEY`, `RENDERER_ENCRYPTION_KEY`. Never
  `APP_KEY`.
- 32 random bytes for the 256-bit ciphers, stored base64 in the secret manager, for example
  `php -r 'echo "base64:".base64_encode(random_bytes(32)), PHP_EOL;'`.
- Both sides read it from their own secret; neither side reads the other's environment.
- The application refuses to boot when a configured relationship has no key.

## Laravel side

```php
use Illuminate\Encryption\Encrypter;
use Illuminate\Support\Str;

$key = base64_decode(Str::after(config('services.connector.key'), 'base64:'), true);
$encrypter = new Encrypter($key, 'aes-256-cbc');   // cipher explicit: the default is aes-128-cbc
$encrypter->previousKeys($previousRawKeys);        // raw bytes, same cipher

$token = $encrypter->encryptString(json_encode([
    'exp' => now()->addMinutes(5)->getTimestamp(),
    'purpose' => 'resource-credentials',
    'jti' => bin2hex(random_bytes(16)),
    'data' => $payload,
], JSON_THROW_ON_ERROR));

$data = json_decode($encrypter->decryptString($incoming), true, 512, JSON_THROW_ON_ERROR);
```

- Bind this encrypter under its own name in the container. The `Crypt` facade and the `encrypt()`/`decrypt()`
  helpers use the application key.
- `decrypt($payload, $unserialize = true)` calls `unserialize()` on the plaintext. Use `decryptString` for
  anything another service produced.
- `aes-256-gcm` is also supported by the framework. Pick one cipher per relationship and check that each
  package supports it.

## Go, Node and Rust side

| Package | String path (use) | Serialize path (avoid across services) | Key default to watch |
|---|---|---|---|
| laravel-go-encryption | `EncryptString`, `DecryptString`, with `encoding/json` | `Encrypt`, `Decrypt` | the quickstart passes `os.Getenv("APP_KEY")` |
| laravel-node-encryption | `encryptString`, `decryptString` | `encrypt`, `decrypt` | the key defaults to `process.env.APP_KEY` when omitted |
| laravel-rust-encryption | `encrypt_string`, `decrypt_string`, with `serde_json` | `encrypt`, `decrypt` | the example reads `APP_KEY` |

All three support previous keys for rotation. Pass the dedicated key explicitly in every constructor.

## Payload shape and receiver checks

```json
{ "exp": 1793450000, "purpose": "resource-credentials", "jti": "9f2c...", "data": { } }
```

The receiver, in this order:

1. `decryptString`; on failure return one opaque error.
2. Decode JSON strictly; reject unknown `purpose`.
3. Reject when `exp` is in the past (allow a small, documented clock skew).
4. For critical payloads, consume `jti` atomically, for example `SET jti:[value] 1 NX EX [seconds until exp]`.
   A failed set means replay: reject.
5. Act on `data`.

## Rotation and failure

- Rotation: add the new key as current and the old one to the previous keys on the receiver first, then on the
  sender. Remove the old key once the longest `exp` window has passed.
- Errors: decrypt failures return a generic message; details go to logs without the payload.
- Fail closed: a credential that is present but cannot be decrypted fails the operation. It never runs without
  the credential.
- TLS stays on every hop. Payload encryption protects the places where TLS ends: queues, logs, caches, spools.

## Interop tests

- CI job one: the real Laravel encrypter produces vectors (string payloads, rotated keys, each cipher you use);
  the other language decrypts them.
- CI job two: the other language encrypts; a PHP script decrypts with `decryptString`.
- Matrix over the Laravel majors you run. The three packages run this in their own CI for Laravel 10 to 13;
  your job proves your key handling and payload shape.
- Measure decrypt cost for your payload size on your own hardware before quoting a number.
