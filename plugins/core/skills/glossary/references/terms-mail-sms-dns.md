# Terms: mail, SMS, DNS and domains

verified 2026-11-04. Identity and category only. Limits, regions and plans change; look them up live.

| term | aliases | what it is | not to confuse with | official URL |
|---|---|---|---|---|
| Brevo | formerly Sendinblue | Marketing and transactional email, SMS and CRM platform; renamed from Sendinblue in 2023 | Sendinblue (old name, same company) | https://www.brevo.com/ |
| Mailjet | - | Email delivery and marketing platform | Mailgun | https://www.mailjet.com/ |
| Postmark | - | Transactional email delivery service | Mailgun | https://postmarkapp.com/ |
| Mailgun | - | Email API for sending and receiving | Mailchimp, Mailjet | https://www.mailgun.com/ |
| SendGrid | Twilio SendGrid | Email delivery platform of Twilio | Twilio SMS | https://sendgrid.com/ |
| rapidmail | - | German newsletter tool | CleverReach | https://www.rapidmail.de/ |
| CleverReach | - | German newsletter and email marketing tool | rapidmail | https://www.cleverreach.com/ |
| seven.io | formerly sms77, seven | SMS and messaging gateway from Germany (seven communications); renamed from sms77 | Twilio | https://www.seven.io/ |
| Twilio | - | Communications API for SMS, voice and more | SendGrid (same group, separate product) | https://www.twilio.com/ |
| WhatsApp Business Platform | WhatsApp Cloud API, WABA | Meta's API for business messaging on WhatsApp, with approved message templates | the WhatsApp Business app | https://developers.facebook.com/docs/whatsapp/cloud-api |
| Mailcow | - | Dockerized self-hosted mail server suite | Postfix alone | https://mailcow.email/ |
| Mailpit | - | Local SMTP server and inbox for development | production mail relay | https://mailpit.axllent.org/ |
| SPF | Sender Policy Framework | DNS record that lists hosts allowed to send mail for a domain (RFC 7208) | DKIM, DMARC | https://www.rfc-editor.org/rfc/rfc7208 |
| DKIM | DomainKeys Identified Mail | Cryptographic mail signature checked via a DNS key (RFC 6376) | SPF | https://www.rfc-editor.org/rfc/rfc6376 |
| DMARC | - | Policy and reporting layer on top of SPF and DKIM (RFC 7489) | SPF, DKIM | https://www.rfc-editor.org/rfc/rfc7489 |
| Double-Opt-In | DOI, Double Opt-in | Consent flow where the address is confirmed by a link in a mail, expected for email marketing in Germany | single opt-in, Opt-out | https://www.gesetze-im-internet.de/uwg_2004/__7.html |
| DENIC | DENIC eG | Registry for the .de top-level domain | a registrar | https://www.denic.de/ |
| INWX | InterNetworX | German domain registrar and DNS provider | DENIC | https://www.inwx.de/ |
| deSEC | - | Non-profit DNS hosting service from Germany | Hetzner DNS | https://desec.io/ |
| RDAP | Registration Data Access Protocol | JSON and HTTP successor of WHOIS (RFC 7480 family) | WHOIS | https://about.rdap.org/ |
| WHOIS | whois | Legacy text protocol for domain registration data (RFC 3912) | RDAP | https://www.rfc-editor.org/rfc/rfc3912 |
| AuthInfo | Auth-Code, EPP-Code, Transfer-Code, Authorization Code | Secret code for transferring a domain to another registrar | API key, 2FA code | https://www.rfc-editor.org/rfc/rfc5731 |
| DNSSEC | - | Signatures for DNS data that protect against forged answers | DoH, DoT | https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en |
| Let's Encrypt | LE | Free certificate authority using ACME | ZeroSSL | https://letsencrypt.org/ |
| ZeroSSL | - | Certificate authority with ACME support | Let's Encrypt | https://zerossl.com/ |
| ACME | - | Protocol for automated certificate issuance (RFC 8555) | a CA product | https://www.rfc-editor.org/rfc/rfc8555 |
