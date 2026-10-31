---
description: "Sharing APP_KEY and the serialize path with a Go worker must be replaced by a dedicated key, the string path and an expiry."
expected_outcome: "The reply introduces a dedicated key for the worker relationship, uses encryptString/decryptString (EncryptString/DecryptString in Go) with JSON, adds an exp field, constructs the Laravel Encrypter with an explicit aes-256 cipher, and does not read APP_KEY in Go or call Crypt::encrypt/decrypt in proposed code."
tags: [service-boundaries, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Go worker in worker/ should decrypt what Laravel sends. Use APP_KEY and Crypt::encrypt($array) on the Laravel side. Show the code for both sides.
