# Collocations and calques: what a native writer would not combine

## Contents

- Why this list exists
- How the numbers were measured
- German: rewrite
- German: established, do not flag
- German: false friends
- English: rewrite
- English: established or regional
- Checking a new candidate
- When the corpus cannot decide

## Why this list exists

Text can be grammatical and still read as translated. In a 2026 study, a classifier flagged 60.2 % of one
model's generated German and 37.6 % of another's as translated, and the human readers who noticed gave
"unusual words or word combinations" as their main reason (Valentini et al., COLM 2026,
https://arxiv.org/html/2608.17399, verified 2026-11-03). A word list does not catch that. A list of
combinations, each checked against a native corpus, does.

The opposite mistake is just as common: flagging a phrase because it looks English. "einmal mehr" is an
example. It occurs half as often as "wieder einmal" in German books, which makes it ordinary German. An earlier
version of this skill flagged it; it no longer does.

## How the numbers were measured

Google Books Ngram, corpus `de-2019` or `en-2019`, case-sensitive, smoothing 0, value for the year 2019, measured
2026-11-03. The ratio compares the flagged phrase with the natural form: "1 : 138" means the natural form
occurs 138 times as often. Books are not UI text, so read the ratio as a comparison of two phrasings, not
as a rate. `scripts/collocation_check.py` repeats any measurement.

Reading the ratio (rule of thumb for this skill, not a published threshold):

| Ratio | Reading |
|---|---|
| 1 : 10 or rarer | calque or unusual combination: rewrite |
| 1 : 3 to 1 : 10 | weak: prefer the natural form in UI, docs and mail; fine in quoted speech |
| above 1 : 3 | established: do not flag on frequency |

`copy_lint.py` flags the rewrite rows as CAL01 and the register notes as CAL02.

## German: rewrite

| Flagged | Natural form | Ratio | Note |
|---|---|---|---|
| eine Entscheidung machen | eine Entscheidung treffen | 1 : 138 | |
| ein Problem adressieren | ein Problem lösen / angehen | 1 : 130 / 1 : 7 | also research numbers from 2026-11-03 |
| Fragen adressieren | Fragen beantworten | 1 : 655 | |
| die Zielgruppe adressieren | die Zielgruppe ansprechen | 1 : 31 | "Kunden adressieren" 1 : 16; "adressiert an" (a letter) is fine |
| Wir sind aufgeregt | Wir freuen uns | 1 : 745 | "aufgeregt" means nervous |
| Ich erinnere das | Ich erinnere mich daran | 1 : 537 | not in the linter: too many legitimate uses of "erinnern" |
| nicht länger verfügbar | nicht mehr verfügbar | 1 : 92 | "nicht länger gültig" 1 : 18 |
| eine gute Zeit haben | Spaß haben, oder sagen, was passiert | 1 : 70 | |
| mehr als glücklich | sehr gern | 1 : 27 | structures differ; read the ratio as a hint |
| Feedback teilen | Feedback geben | not found : found | the corpus has no hit for the calque |
| Wert hinzufügen | Wert schaffen, or say what it brings | 1 : 11 | |
| Zeit einsparen | Zeit sparen | 1 : 8 | |
| Hab einen schönen Tag | Schönen Tag noch | 1 : 5 | |
| am Ende des Tages (figurative) | letzten Endes, letztlich | 1 : 4 | the literal "end of the day" is fine |
| in 2026 | 2026, im Jahr 2026 | 1 : 4 (in 2019) | |
| für mehrere Minuten | mehrere Minuten lang | 1 : 3 | listed as an error in the Microsoft German style guide |
| Für weitere Informationen kontaktieren Sie ... | Wenn du Fragen hast, schreib uns an ... | not measured | Microsoft German style guide lists it as an English syntax pattern |

## German: established, do not flag

| Phrase | Compared with | Ratio | Note |
|---|---|---|---|
| einmal mehr | wieder einmal | 1 : 2 | ordinary German |
| macht Sinn / Sinn machen | ergibt Sinn / Sinn ergeben | 2 : 1 / 1 : 1 | Duden marks it colloquial, after English "make sense" (https://www.duden.de/rechtschreibung/Sinn, verified 2026-11-03 in the research). Fine in chat-like copy, not in docs or legal text. CAL02 |
| eine Erfahrung machen | Erfahrung sammeln | 6.5 : 1 | ordinary German |
| in Kontakt bleiben | in Verbindung bleiben | 1.8 : 1 | |
| eine Nachricht erhalten | eine Nachricht bekommen | 1.6 : 1 | both normal; "bekommen" is closer to speech, so it often fits UI better. A register choice, not a calque |
| zur Verfügung stellen | bereitstellen | 1.3 : 1 | frequent, but still nominal style: in UI prefer a verb ("Du kannst ... herunterladen"). FVG01 |
| in Echtzeit | in Realzeit | 84 : 1 | ordinary German |

## German: false friends

No corpus helps here, because both words are normal German. Read the sentence for meaning.

| Wrong when it means | German word | Write instead |
|---|---|---|
| eventually | eventuell (= possibly) | schließlich, irgendwann |
| actually | aktuell (= current) | eigentlich, tatsächlich |
| billion | Billion (= 10^12) | Milliarde |
| become (in "you will become an email") | — | bekommen ↔ get, the mirror case in English below |

Sources: humanizer-de pattern 45 (https://github.com/marmbiz/humanizer-de) and the Microsoft German style guide
(https://aka.ms/german-styleguide), both verified 2026-11-03 in the research.

## English: rewrite

These are the calques German speakers bring into English, plus the corporate combinations models produce.

| Flagged | Natural form | Ratio |
|---|---|---|
| since three years | for three years | 1 : 345 |
| discuss about the | discuss the | 1 : 144 |
| looking forward to hear | looking forward to hearing | 1 : 40 |
| make a photo | take a photo | 1 : 39 |
| explain me | explain to me | 1 : 23 |
| informations, feedbacks, advices | information, feedback, advice | informations 1 : 1350 |
| on a daily basis | every day, daily | 1 : 11 |
| with regards to | with regard to, or about | 1 : 11 |
| in a timely manner | promptly, or the actual time ("within two hours") | 1 : 9 |
| on the picture | in the picture | 1 : 7 |
| deliver value / provide value | say what the reader gets ("add value" is the idiom) | 1 : 7 / 1 : 6 |
| you will become an email | you will get an email | not found : found |

## English: established or regional

| Phrase | Ratio | Note |
|---|---|---|
| take a decision | 1 : 19 against "make a decision" | British usage. Fine for a UK audience; for US or mixed audiences write "make". CAL02 |
| the possibility to | 1.2 : 1 against "the option to" | not a calque by frequency; "you can" is often shorter |
| until Friday | 1 : 1 against "by Friday" | both normal, different meaning: "until" is a duration, "by" a deadline. German "bis" covers both, so check the meaning |

## Checking a new candidate

1. Write the flagged phrase and the form you would expect a native writer to use, both in the same grammatical
   shape (infinitive against infinitive, same article).
2. Run `python3 scripts/collocation_check.py --lang de "Phrase" "Alternative"`.
3. Rewrite at 1 : 10 or rarer. Between 1 : 3 and 1 : 10, decide by register. Above 1 : 3, leave it.
4. When the owner corrects the same combination twice, add it to the product glossary (`avoid` column) so
   the linter catches it in that product. Propose it for this list only when it is a calque in general.

## When the corpus cannot decide

- The phrase has more than five words, or contains a comma: the corpus stores at most 5-grams.
- One phrase is part of the other ("den Link klicken" inside "auf den Link klicken"): the shorter is counted
  inside the longer, so the ratio says nothing.
- Both phrases are rare, or both are missing: no verdict. Ask a native speaker or check DWDS
  (https://www.dwds.de/wp/ for German collocations, verified 2026-11-03 in the research).
- The endpoint is offline: the script prints "no verdict". Do not fill in a number from memory.
