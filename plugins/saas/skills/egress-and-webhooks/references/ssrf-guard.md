# SSRF guard

Load when building or reviewing the egress client, its range table, URL canonicalization or tests. Ranges come from
the IANA special-purpose registries, read 2026-11-03; re-read them when you update the table.

## Contents

- Pipeline
- Range table
- Canonicalization inputs to refuse
- Reason codes
- Tests

## Pipeline

1. Parse with one URL parser. Keep the parsed object; never rebuild the request from the original string.
2. Canonicalize: lowercase scheme and host, IDNA to ASCII, strip one trailing dot, refuse anything listed under
   "Canonicalization inputs to refuse".
3. Refuse blocked hostnames before resolving (`localhost`, `*.localhost`, metadata hostnames, internal suffixes
   such as the cluster domain).
4. Resolve with the application's resolver, not the system hosts file. Collect all A and AAAA answers.
5. Classify every answer. Strict mode: refuse when any answer is blocked. Pick one allowed address and pin it.
6. Connect to the pinned address; use the hostname for SNI, certificate checks and `Host`.
7. Dial hook: check the socket address again against the same table.
8. Redirect hook: off, or for each hop run steps 1 to 7 again and count hops.
9. Read the body through a limit placed after decompression; read limit plus one byte to detect overflow.

## Range table

<!-- lint-allow: L13 the table lists IANA special-purpose ranges the guard must refuse -->
| Block | Name | Source |
|---|---|---|
| `0.0.0.0/8` | "This network" <!-- lint-allow: L13 IANA range --> | RFC 791 |
| `10.0.0.0/8` | Private-Use <!-- lint-allow: L13 IANA range --> | RFC 1918 |
| `100.64.0.0/10` | Shared Address Space (CGNAT) <!-- lint-allow: L13 IANA range --> | RFC 6598 |
| `127.0.0.0/8` | Loopback | RFC 1122 |
| `169.254.0.0/16` | Link Local, includes cloud metadata <!-- lint-allow: L13 IANA range --> | RFC 3927 |
| `172.16.0.0/12` | Private-Use <!-- lint-allow: L13 IANA range --> | RFC 1918 |
| `192.0.0.0/24` | IETF Protocol Assignments <!-- lint-allow: L13 IANA range --> | RFC 6890 |
| `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | Documentation | RFC 5737 |
| `192.88.99.0/24` | Deprecated 6to4 relay anycast <!-- lint-allow: L13 IANA range --> | RFC 7526 |
| `192.168.0.0/16` | Private-Use <!-- lint-allow: L13 IANA range --> | RFC 1918 |
| `198.18.0.0/15` | Benchmarking <!-- lint-allow: L13 IANA range --> | RFC 2544 |
| `224.0.0.0/4` | Multicast <!-- lint-allow: L13 IANA range --> | RFC 5771 |
| `240.0.0.0/4` | Reserved <!-- lint-allow: L13 IANA range --> | RFC 1112 |
| `255.255.255.255/32` | Limited Broadcast <!-- lint-allow: L13 IANA range --> | RFC 919 |
| `::/128`, `::1/128` | Unspecified, Loopback | RFC 4291 |
| `::ffff:0:0/96` | IPv4-mapped; decode and check the IPv4 part <!-- lint-allow: L13 IANA range --> | RFC 4291 |
| `64:ff9b::/96`, `64:ff9b:1::/48` | IPv4-IPv6 translation; decode and check <!-- lint-allow: L13 IANA range --> | RFC 6052, RFC 8215 |
| `100::/64` | Discard-only <!-- lint-allow: L13 IANA range --> | RFC 6666 |
| `2001::/32` | Teredo <!-- lint-allow: L13 IANA range --> | RFC 4380 |
| `2001:db8::/32`, `3fff::/20` | Documentation <!-- lint-allow: L13 IANA range --> | RFC 3849, RFC 9637 |
| `2002::/16` | 6to4; the next 32 bits are an IPv4 address <!-- lint-allow: L13 IANA range --> | RFC 3056 |
| `fc00::/7` | Unique-Local <!-- lint-allow: L13 IANA range --> | RFC 4193 |
| `fe80::/10` | Link-Local <!-- lint-allow: L13 IANA range --> | RFC 4291 |
| `ff00::/8` | Multicast <!-- lint-allow: L13 IANA range --> | RFC 4291 |
| operator ranges | pod, service and VPC networks, internal load balancers | own config |

The multicast rows come from RFC 5771 and RFC 4291, not from the special-purpose registry. The simplest complete
rule: allow only addresses the IANA registries mark as globally reachable, then subtract the operator ranges.

## Canonicalization inputs to refuse

- Schemes other than `http` and `https` (`file`, `gopher`, `ftp`, `dict`, `data`).
- Userinfo (`user:pass@host`), backslashes, whitespace, control characters, encoded CR or LF in any part.
- Hosts written as one decimal number, octal or hex parts, or fewer than four IPv4 parts.
- IPv6 zone identifiers (`%eth0`).
- Ports outside the allowed list for the feature.
- Hosts that the parser and the HTTP client read differently; test with both.

## Reason codes

Return a closed enum, for example `scheme_not_allowed`, `userinfo`, `bad_host`, `port_not_allowed`,
`blocked_address`, `mixed_answers`, `no_address`, `redirect_blocked`, `too_many_redirects`, `timeout`,
`body_too_large`. Show the code to the user; log the resolved address only in internal logs.

## Tests

- One case per range row, plus mapped (`::ffff:` prefix with a loopback IPv4) and translated forms.
- Rebinding: resolver returns a public then a blocked address; no blocked connection, reason `mixed_answers` in
  strict mode.
- Dial hook: bypass resolution; the hook refuses a blocked socket address.
- Redirect: public test server answers 302 to a blocked URL; refused with `redirect_blocked`.
- Slow body and compression bomb: cut at the total timeout and the decompressed cap.
- A self-test that feeds a known-blocked address and fails if the guard accepts it, so a misconfigured table
  cannot pass silently.
