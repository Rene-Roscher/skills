# EU digital regulations for a SaaS

## Contents

- Dates at a glance
- Digital Services Act (hosting user content)
- Data Act (cloud switching)
- NIS2 and the German BSIG
- Cyber Resilience Act
- AI Act

Review-ready draft, not legal advice. Scope: EU, with the German NIS2 implementation. Regulation text read from
the Official Journal versions (EUR-Lex, Publications Office) on 2026-11-03. Each regulation is amended often;
re-check the consolidated text before relying on a date that lies within a year.

## Dates at a glance

| Regulation | Date | What applies |
|---|---|---|
| DSA (EU) 2022/2065 | 17 February 2024 | all duties for intermediary and hosting services (Art. 93) |
| Data Act (EU) 2023/2854 | 12 September 2025 | general application, including Chapter VI switching (Art. 50) |
| Data Act | 12 January 2027 | no switching charges at all (Art. 29(1)) |
| Data Act | 12 September 2027 | Chapter IV (unfair B2B data terms) for older indefinite or long contracts (Art. 50) |
| NIS2UmsuCG, BSIG | 6 December 2025 | German NIS2 rules in force; BSI portal open since 6 January 2026 (BSI press release) |
| CRA (EU) 2024/2847 | 11 June 2026 | conformity assessment bodies (Chapter IV) |
| CRA | 11 September 2026 | manufacturer reporting of exploited vulnerabilities and severe incidents (Art. 14) |
| CRA | 11 December 2027 | everything else (Art. 71) |
| AI Act (EU) 2024/1689 | 2 February 2025 | Chapters I and II: AI literacy (Art. 4), prohibited practices |
| AI Act | 2 August 2025 | general-purpose AI model duties (Chapter V), penalties |
| AI Act | 2 August 2026 | general application, including Art. 50 transparency |
| AI Act, as amended by (EU) 2026/1744 | 2 December 2026 | Art. 50(2) marking for generative systems already on the market before 2 August 2026 |
| AI Act, as amended by (EU) 2026/1744 | 2 December 2027 / 2 August 2028 | high-risk duties for Annex III / Annex I systems |

## Digital Services Act (hosting user content)

Applies to any hosting service, whatever its size: comments, boards, shared files, public profiles, uploaded
content visible to others, also behind a login.

| Article | Duty | Build |
|---|---|---|
| 11 | single point of contact for authorities, with languages | contact page entry, monitored mailbox |
| 12 | single point of contact for users, not only automated | contact page entry, human reachable |
| 14 | content restrictions and moderation in the terms; inform users of significant changes | numbered moderation clauses |
| 16 | notice and action: reason, exact URL, name and email, good-faith statement; receipt confirmation | notice form or endpoint, moderation queue |
| 17 | statement of reasons for removal, demotion, payment limits, suspension | decision record with ground and redress |
| 18 | inform law enforcement promptly of suspected crimes threatening life or safety | escalation path in the moderation runbook |

The exemption for micro and small enterprises (Art. 19) covers only the online-platform section, not Art.
11-18. The moderation record design and the privacy side are in `gdpr-engineering` (ugc-dsa reference). The
German enforcement and supervisory rules are in the DDG.

## Data Act (cloud switching)

- A "data processing service" is a digital service that gives on-demand network access to a shared pool of
  configurable, scalable and elastic computing resources (Art. 2). Whether a given SaaS fits is a legal
  question; most multi-tenant SaaS products are treated as in scope in the commentary (Unverified against an
  authority statement).
- Contract terms (Art. 25): written contract available before signing; switching or export on request; notice
  period at most two months; transitional period at most 30 days (alternative up to seven months only if
  technically unfeasible, notified within 14 working days); exhaustive list of exportable data; retrieval
  period of at least 30 days; full erasure afterwards; switching charges per Art. 29.
- Charges (Art. 29): reduced charges, not above the direct cost of switching, allowed until 12 January 2027;
  none after that. Standard fees, early termination penalties and switching charges are disclosed before the
  contract.
- Interfaces (Art. 30(2)): providers other than pure infrastructure make open interfaces available free of
  charge to customers and destination providers.
- Exemptions (Art. 31): services mostly custom-built for one customer and not offered at broad commercial
  scale are exempt from some duties; non-production test versions for a limited time are exempt from the
  chapter. The customer is told which duties do not apply.
- Pending: the Commission's Digital Omnibus proposes lighter rules for SMEs and custom services. As of
  2026-11-03 no adopted text was found (Unverified; secondary sources only).

## NIS2 and the German BSIG

- In force in Germany since 6 December 2025 (BSI press release of 5 December 2025), with no general transition
  period.
- Sectors relevant to a SaaS (BSIG Anlage 1, Digitale Infrastruktur): 6.1.4 "Anbieter von
  Cloud-Computing-Diensten", 6.1.10 "Managed Services Provider", 6.1.11 "Managed Security Services Provider".
  NIS2 defines a cloud computing service as one enabling on-demand administration and broad remote access to a
  scalable and elastic pool of shareable computing resources; CRA Recital 12 states that NIS2 applies to SaaS,
  PaaS and IaaS. Whether your product is such a service is for the lawyer.
- Size (BSIG § 28): important entity in Annex 1 or 2 sectors with at least 50 employees, or both turnover and
  balance sheet above EUR 10 million; especially important from 250 employees, or turnover above EUR 50
  million and balance sheet above EUR 43 million. Negligible side activities can be disregarded (Abs. 3).
  Linked and partner enterprises are counted under Recommendation 2003/361/EC unless IT is independent (Abs. 4).
- Registration (BSIG § 33): within three months of first qualifying, through the BSI portal; name, legal form,
  register number, address and contacts including public IP ranges, sector, Member States served, competent
  authorities.
- Reporting (BSIG § 32): significant incident early warning within 24 hours, notification within 72 hours,
  final report one month after the notification (progress report if still ongoing).
- Risk management, management liability and training duties exist as well (BSIG §§ 30, 38); not re-read here
  (Unverified).

## Cyber Resilience Act

- A "product with digital elements" is software or hardware and its remote data processing solutions (Art. 3).
  Remote data processing is in scope only when the manufacturer designed it and the product cannot perform a
  function without it (Recital 12, Art. 3).
- Shipping an agent, CLI, SDK, desktop or mobile app makes you a manufacturer; the API it needs is in scope as
  remote data processing. A web-only SaaS and websites that do not support a product's function are not in
  scope (Recital 12).
- Reporting from 11 September 2026 (Art. 14), through the single reporting platform, to the coordinating CSIRT
  and ENISA: actively exploited vulnerability early warning within 24 hours, notification within 72 hours,
  final report within 14 days after a fix is available; severe incident early warning within 24 hours,
  notification within 72 hours, final report within one month.
- Product requirements, vulnerability handling, support period and conformity assessment apply from 11
  December 2027. Release mechanics (SBOM, signing) are in `release-supply-chain` if installed.

## AI Act

- Roles: the provider develops an AI system or model and places it on the market under its own name; the
  deployer uses one under its authority. A SaaS that builds a chat assistant on a third-party model and offers
  it to customers is usually the provider of that AI system; its customers are deployers. Confirm the role
  with the lawyer and write it into the AI register.
- AI literacy (Art. 4, as amended by (EU) 2026/1744): take measures to support AI literacy of staff and others
  operating the system; no specific level is required of any individual.
- Art. 50(1): inform people that they interact with an AI system unless it is obvious.
- Art. 50(2): providers of systems generating synthetic audio, image, video or text mark outputs in a
  machine-readable, detectable way; not for assistive standard editing that does not substantially alter the
  input. Systems on the market before 2 August 2026 comply by 2 December 2026 (Art. 111(4) as amended).
- Art. 50(4): deployers disclose deepfakes, and AI-generated text published to inform the public on matters of
  public interest unless a person holds editorial responsibility after human review.
- Art. 50(5): the information is given clearly at the latest at the first interaction and meets accessibility
  requirements.
- General-purpose AI models (Chapter V, since 2 August 2025) bind the model provider. When fine-tuning makes a
  downstream company a model provider is set out in Commission guidance not fetched here (Unverified).
- Check every AI feature against prohibited practices (Art. 5) and high-risk uses (Annex III, for example
  employment and worker management, credit scoring, education). A hit changes the regime; stop and involve the
  lawyer.
