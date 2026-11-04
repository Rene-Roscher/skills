---
type: llm
weight: 3
focus:
  source: file
  path: docs/GLOSSARY.md
---

PASS if docs/GLOSSARY.md still has the original Buchung row and gains one new row for Kasse in the same five-column table, whose meaning says it is the Mollie checkout page and whose "not to confuse with" column mentions the ERP cash register module. FAIL if the file is unchanged, the table is broken, or the row holds anything beyond the owner's explanation.
