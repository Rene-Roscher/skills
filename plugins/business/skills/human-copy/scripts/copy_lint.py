#!/usr/bin/env python3
"""Flag copy patterns that make English or German text read as generic, unsourced or machine-made.

Usage:
  copy_lint.py [--lang en|de|auto] [--strict] [--glossary FILE] FILE [FILE ...]
  copy_lint.py [--lang en|de|auto] [--strict] [--glossary FILE] -        (read stdin)
  copy_lint.py --voice-check DIR        (check a product's voice files, for example docs/voice)
  copy_lint.py --self-test

Every finding is a warning. Exit code is 0 unless --strict is given and at least one warning was
printed (then 1). A usage error exits 2, a failed --self-test exits 1.

What it checks (code, meaning):
  SUP01  superlative, "only", "first" or absolute claim without a source marker (link, "according to",
         "benchmark", "laut") in the same sentence; a bare digit does not count as a source
  CLM01  benefit or comparison verb without a number or a stated mechanism
  TEL01  core tell word (any hit)          TEL02  soft tell word (density, or any hit in a heading)
  TEL03  marketing filler (any hit)        TEL04  tell phrase or sentence template (any hit)
  OPN01  generic opener in the first 250 characters
  NXY01  "not X but Y" contrast (density, or any hit in a heading or the first sentence)
  TRI01  staccato triad such as "Fast. Simple. Secure."
  DSH01  em dash density (EN) or any em dash (DE)    DSH02  dash followed by a comma
  DSH03  paired dash insertion (house style, German)
  TTL01  title-case heading (EN) or capitalised function word in a heading (DE)
  RES01  chat residue or placeholder          EXC01  more than one exclamation mark
  EMO01  emoji at the start of a line         LEN01  more than 15 % of sentences over 25 words
  CTA01  generic link or button label         TST01  testimonial that needs a source record
  CNT01  customer or user count ("trusted by over N teams") that needs a dated source record
  CAL01  calque or unidiomatic combination, with the corpus ratio against the natural form (EN and DE)
  CAL02  register note: colloquial or regional, fine in chat-like copy, not in docs or legal text
  GLO01  variant the product glossary forbids (only with --glossary)
  German only: TYP01 English quotes, TYP02 apostrophe before -s, TYP03 split compound,
  TYP04 punctuation after a label ending in ? ! ..., TYP05 number or currency format,
  ADR01 du and Sie mixed, ADR02 capitalised Du mid-sentence,
  FVG01 nominal style, CON01 connector at sentence start (density).

--voice-check DIR reports VOI01 (malformed corrections.jsonl line), VOI02 (a correction rule seen twice or
more that is not yet promoted to the glossary or a lint rule), VOI03 (missing voice file or no approved
examples) and VOI04 (an email address or phone number in a correction: personal data does not belong there).

The word lists are calibrated against a field guide and corpus studies, not proof of authorship.
A hit is a prompt to rewrite the sentence with a fact; the lists drift with each model generation.
Word lists last reviewed: 2026-11-03. Calque ratios: Google Books Ngram, corpora de-2019 and en-2019,
year 2019, measured 2026-11-03 (scripts/collocation_check.py repeats a measurement).

Python 3.8 or later, standard library only, no network.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

WORDLIST_REVIEWED = "2026-11-03"
I = re.IGNORECASE


def rx(pattern, flags=I):
    return re.compile(pattern, flags)


# --- source markers -------------------------------------------------------------------------

SRC_EN = rx(r"https?://|\[\d+\]|\b(?:source|according to|survey|benchmark|measured|audit|as of|certified|ranked by)\b")
SRC_DE = rx(r"https?://|\[\d+\]|\b(?:quelle|laut|gemäß|umfrage|benchmark|gemessen|messung|auswertung|stand|zertifiziert)\b")
MECH_EN = rx(r"\b(?:because|by (?:\w+ing|using|running|checking)|so that|instead of|which means)\b")
MECH_DE = rx(r"\b(?:weil|indem|durch|damit|dadurch|statt)\b")

# --- superlatives and absolute claims -------------------------------------------------------

SUP_EN = rx(
    r"(?<!\bat )\b(?:best(?! (?:practices?|efforts?|regards|of|way|fit|guess))"
    r"|fastest|easiest|simplest|cheapest|safest|biggest|largest|greatest|smartest"
    r"|most (?:powerful|secure|reliable|advanced|popular|trusted|complete|flexible|innovative|comprehensive|intuitive)"
    r"|(?:the|a|an|our|market|industry|world)[- ]leading|#1|number[- ]one|unrivall?ed|unmatched|the ultimate)\b"
    r"|\bthe only (?!way\b|thing\b|option\b|difference\b|catch\b|exception\b|reason\b|requirement\b)\w+(?: \w+){0,2} (?:that|to|which|who|with)\b"
    r"|\bworld's first\b|\bthe first (?:\w+ ){0,3}(?:to|that|which)\b|\bfirst[- ]ever\b"
    r"|\b(?:best|biggest|largest|fastest|greatest)\b[^.!?]{0,30}\bever\b"
    r"|\b100 ?% (?:secure|reliable|uptime|accurate|safe)\b|\bguaranteed\b|\brisk[- ]free\b|\bzero downtime\b"
)
SUP_DE = rx(
    r"\b(?:die|der|das|den|dem|unser\w*|dein\w*)\s+(?:beste[nrms]?|schnellste[nrms]?|einfachste[nrms]?|günstigste[nrms]?"
    r"|sicherste[nrms]?|größte[nrms]?|zuverlässigste[nrms]?|leistungsstärkste[nrms]?|führende[nrms]?|innovativste[nrms]?)\b"
    r"|\bNr\.?\s?1\b|\bmarktführ\w*|\bMarktführer\w*|\bweltweit (?:führend|einzigartig|größt|beste)\w*"
    r"|\beinzigartig\w*|\bunübertroffen\w*|\bunschlagbar\w*|\bweltweit erste\w*|\baller Zeiten\b"
    r"|\b(?:der|die|das) einzige\b(?! Weg| Unterschied| Grund| Haken)|\b(?:optimal|ideal)ste\w*|\beinzigste\w*|\bgrößtmöglichst\w*"
    r"|\b100 ?% (?:sicher|zuverlässig|verfügbar|genau)\b|\bgarantiert\b|\brisikofrei\b"
)

# --- benefit claims without a number --------------------------------------------------------

CLM_EN = rx(
    r"\b(?:faster|quicker|reduc(?:e|es|ed|ing)|increas(?:e|es|ed|ing)|improv(?:e|es|ed|ing)|cuts?|boosts?|boosting"
    r"|saves? (?:you |your |\w+ )?(?:time|money|hours|effort)|more efficient|better performance)\b"
)
CLM_DE = rx(r"\b(?:schneller|effizienter|spart|sparen|reduziert|reduzieren|steigert|erhöht|verbessert|verkürzt|senkt)\b")

# --- tell lists (reviewed 2026-11-01) -------------------------------------------------------

TEL_EN_CORE = rx(
    r"\b(?:delv(?:e|es|ed|ing)|tapestr(?:y|ies)|testament to|underscor(?:es|ed|ing)|showcas(?:e|es|ed|ing)"
    r"|intricate|intricacies|pivotal|meticulous(?:ly)?|garner(?:s|ed|ing)?|vibrant|realm|commendable|camaraderie"
    r"|palpable|multifaceted|bolster(?:s|ed|ing)?|interplay|boasts an?)\b"
)
TEL_EN_SOFT = rx(
    r"\b(?:crucial|foster(?:s|ed|ing)?|enhanc(?:e|es|ed|ing)|align(?:s|ed)? with|landscape|robust|seamless(?:ly)?"
    r"|leverag(?:e|es|ed|ing)|navigat(?:e|es|ing) the|deep dive|paving the way|valuable insights?|empower(?:s|ed|ing)?"
    r"|streamlin(?:e|es|ed|ing)|unlock(?:s|ed|ing)?|dependable|meaningful|facilitat(?:e|es|ed|ing)|utili[sz](?:e|es|ed|ing))\b"
)
TEL_EN_MKT = rx(
    r"\b(?:cutting[- ]edge|state[- ]of[- ]the[- ]art|next[- ]gen(?:eration)?|world[- ]class|best[- ]in[- ]class"
    r"|game[- ]chang(?:er|ing)|revolutioni[sz](?:e|es|ed|ing)|supercharg(?:e|es|ed|ing)|effortless(?:ly)?"
    r"|industry[- ]leading|award[- ]winning|thought leader|unlock the power|next level|one-stop shop"
    r"|end-to-end solution)\b"
)
TEL_EN_PHRASE = [
    (rx(r",\s+(?:highlighting|underscoring|emphasi[sz]ing|showcasing|ensuring|reflecting|symboli[sz]ing|fostering"
        r"|enhancing|contributing to|cementing|solidifying)\b"), "trailing participle that only comments"),
    (rx(r"\b(?:serves as|stands as|functions as|is a testament|marks? a (?:pivotal|significant|major|key)"
        r" (?:moment|shift|milestone|turning point)|setting the stage|evolving landscape|ever[- ](?:changing|evolving)"
        r"|plays? an? (?:crucial|pivotal|vital|key|significant|central) role|indelible mark|deeply rooted)\b"),
     "significance puffery"),
    (rx(r"\b(?:matters because|why (?:this|it) matters|here'?s why|here'?s the thing|the distinction matters)\b"),
     "importance flag"),
    (rx(r"\bwithout (?:sacrificing|compromising|trading off|giving up)\b"), "tradeoff denial without a measurement"),
    (rx(r"\brather than (?:merely|simply|just)\b|\bnot simply\b|\binstead, it(?:'s| is)\b"), "corrective framing"),
    (rx(r"\b(?:experts (?:say|agree|argue|believe)|studies (?:show|suggest)|industry (?:reports|experts)"
        r"|observers (?:have )?(?:noted|cited)|(?:many|most) (?:users|customers|teams) (?:say|report|agree|love))\b"),
     "vague attribution"),
    (rx(r"\b(?:it'?s (?:important|worth) (?:to note|noting)|it is (?:important|worth) (?:to note|noting)"
        r"|may potentially|could potentially|based on (?:the )?available information)\b"), "hedge"),
    (rx(r"\bwhether you'?re (?:a|an)\b"), "audience sweep"),
    (rx(r"\b(?:oops|whoops|uh-oh)\b"), "joke or apology in place of the message: say what happened"),
    (rx(r"(?:^|[.!?]\s+)(?:in summary|in conclusion|overall|ultimately|in short|all in all|at the end of the day)\b"),
     "summary opener"),
]
TRANSITION_EN = rx(r"(?:^|[.!?]\s+)(?:additionally|furthermore|moreover|notably|importantly|looking ahead|together, these)\b")

TEL_DE_PHRASE = [
    (rx(r"\bnahtlos\w*|\bmaßgeschneidert\w*|\bganzheitlich\w*|\bMehrwert\w*|\brevolution(?:är\w*|ier\w*)"
        r"|\bgame-?changer\b|\b(?:aufs|auf das) nächste Level\b|\bintegraler Bestandteil\b|\bvielfältige(?:n)? Möglichkeiten\b"
        r"|\beine Vielzahl (?:von|an)\b|\bperfekt geeignet\b|\boptimal abgestimmt\b|\bim Herzen (?:von|des|der)\b"
        r"|\batemberaubend\w*|\bim Fokus\b|\bfokussier\w*"), "buzzword"),
    (rx(r"\bin der heutigen (?:schnelllebigen |digitalen )?(?:Zeit|Welt)\b|\btauch(?:e|t|en)? (?:\w+ )?(?:ein|tief)\b"
        r"|\beintauchen\b"), "stock opener or calque of 'dive in'"),
    (rx(r"\bspielt eine (?:wichtige|entscheidende|zentrale|bedeutende|wesentliche) Rolle\b|\bunterstreicht\b"
        r"|\bes ist (?:wichtig|bemerkenswert|entscheidend) zu (?:beachten|betonen|bemerken|bedenken)\b"
        r"|\bzusammenfassend\b|\bletztlich hängt es\b|\b(?:gewährleistend|hervorhebend|betonend|widerspiegelnd|unterstreichend)\b"),
     "significance, summary or participle tail"),
    (rx(r"\b(?:Experten|Studien|Untersuchungen|Branchenberichte|Kritiker|Beobachter)\s+"
        r"(?:zeigen|sind sich einig|belegen|argumentieren|haben gezeigt|betonen)\b"), "vague attribution"),
    (rx(r"\b(?:könnte|könnten|würde|würden|potenziell|möglicherweise)\b[^.!?]{0,80}"
        r"\b(?:in vielen Fällen|je nach|potenziell|möglicherweise|unter Umständen)\b"), "hedge stack"),
    (rx(r"(?:^|[.!?]\s+)(?:Egal,? ob|Ob)\b[^.!?]{1,80}\boder\b[^.!?]{1,80}[–—:]"), "'Egal ob ... oder' sweep"),
    (rx(r"\b(?:Ups|Hoppla|Huch|Oops)\b"), "joke or apology in place of the message: say what happened"),
]
# Calques and unidiomatic combinations. Each entry: pattern, natural form, corpus ratio (phrase : natural
# form, Google Books Ngram, year 2019, measured 2026-11-03). Only pairs at 1 : 3 or rarer are listed;
# "einmal mehr" (1 : 2 against "wieder einmal") is established German and is not flagged.
CAL_DE = [
    (rx(r"\bEntscheidung(?:en)?\s+(?:zu\s+)?mach\w*|\bmach\w*\s+(?:\w+\s+){0,3}Entscheidung(?:en)?\b"),
     "Entscheidung treffen", "1 : 138"),
    (rx(r"\badressier\w*\b(?!\s+an\b)"),
     "lösen, angehen, beantworten oder ansprechen", "Problem 1 : 130, Fragen 1 : 655, Zielgruppe 1 : 31"),
    (rx(r"\bwir\s+sind\s+(?:so\s+|sehr\s+|super\s+|total\s+)?aufgeregt\b"), "wir freuen uns", "1 : 745"),
    (rx(r"\bnicht\s+länger\s+(?:verfügbar|gültig|möglich|aktiv|unterstützt|erforderlich|nötig|benötigt|erreichbar)\b"),
     "nicht mehr", "verfügbar 1 : 92, gültig 1 : 18"),
    (rx(r"\bfür\s+(?:mehrere|einige|ein paar|wenige)\s+(?:Sekunden|Minuten|Stunden|Tage|Wochen|Monate)\b"),
     "mehrere Minuten lang, oder die Dauer ohne 'für'", "1 : 3; Microsoft German guide lists it as an error"),
    (rx(r"\bin\s+(?:19|20)\d\d\b(?![./-]\d)"), "2026 oder im Jahr 2026 (ohne 'in')", "1 : 4"),
    (rx(r"\bam Ende des Tages\b"), "letzten Endes, letztlich (außer im wörtlichen Sinn)", "1 : 4"),
    (rx(r"\bFeedback\s+(?:mit\s+\w+\s+)?(?:zu\s+)?teil\w*|\bteil\w*\s+(?:\w+\s+){0,2}Feedback\b"),
     "Feedback geben", "phrase absent from the corpus"),
    (rx(r"\bWert\s+(?:zu\s+)?hinzu(?:zu)?füg\w*"), "Wert schaffen, oder sagen, was es bringt", "1 : 11"),
    (rx(r"\bgute Zeit\s+(?:zu\s+)?hab\w*|\bhab\w*\s+(?:\w+\s+){0,2}gute Zeit\b"), "Spaß haben", "1 : 70"),
    (rx(r"\bhab(?:t|en)?\s+(?:einen\s+)?schönen Tag\b"), "Schönen Tag noch", "1 : 5"),
    (rx(r"\bmehr als glücklich\b"), "sehr gern", "1 : 27"),
    (rx(r"\bZeit\s+ein(?:zu)?spar\w*"), "Zeit sparen", "1 : 8"),
]
CAL_DE_NOTE = [
    (rx(r"\bSinn\s+(?:zu\s+)?mach\w*|\bmach(?:t|en|te|ten)\b[^.!?]{0,25}\bSinn\b"),
     "'Sinn machen' is colloquial per Duden (after English 'make sense'); in docs and legal text write 'ergibt Sinn' "
     "or 'ist sinnvoll' (corpus 1 : 1, so not an error)"),
]
CAL_EN = [
    (rx(r"\bsince\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|several|many)\s+(?:years?|months?|weeks?|days?|hours?)\b"),
     "for three years", "1 : 345"),
    (rx(r"\bdiscuss(?:es|ed|ing)?\s+about\b"), "discuss the", "1 : 144"),
    (rx(r"\bexplain(?:s|ed|ing)?\s+(?:me|us|him|her|them)\b"), "explain to me", "1 : 23"),
    (rx(r"\bmak(?:e|es|ing)\s+(?:a\s+)?(?:photos?|pictures?|screenshots?)\b"), "take a photo", "1 : 39"),
    (rx(r"\blook(?:ing)? forward to\s+(?:hear|see|meet|work|welcome|receive|talk)\b"), "looking forward to hearing", "1 : 40"),
    (rx(r"\b(?:informations|feedbacks|advices|softwares)\b"), "the uncountable form (information, feedback)", "informations 1 : 1350"),
    (rx(r"\bon the (?:picture|screenshot|photo|image)\b"), "in the picture", "1 : 7"),
    (rx(r"\bwith regards to\b"), "with regard to, or about", "1 : 11"),
    (rx(r"\b(?:will|you'll|you)\s+become\s+(?:an?\s+)?(?:email|e-mail|message|notification|invoice|reminder|link|code)\b"),
     "get or receive (German 'bekommen' is not 'become')", "phrase absent from the corpus"),
    (rx(r"\b(?:deliver(?:s|ed|ing)?|provid(?:e|es|ed|ing)|driv(?:e|es|ing))\s+(?:real\s+|more\s+)?value\b"),
     "say what the reader gets; the idiom is 'add value'", "deliver value 1 : 7, provide value 1 : 6"),
    (rx(r"\bon a (?:daily|weekly|monthly|regular) basis\b"), "daily, every week, regularly", "on a daily basis vs every day 1 : 11"),
    (rx(r"\bin a timely manner\b"), "promptly, or the actual time", "1 : 9"),
]
CAL_EN_NOTE = [
    (rx(r"\btak(?:e|es|ing)\s+(?:a|the)\s+decision\b"),
     "'take a decision' is British usage; in US English or mixed audiences write 'make a decision' (corpus 1 : 19)"),
]
FVG_DE = rx(
    r"\bzur Verfügung (?:stellen|gestellt)\b|\bin Kenntnis setzen\b|\bzum Abschluss bringen\b|\beiner Prüfung unterziehen\b"
    r"|\bMöglichkeit (?:bieten|eröffnen)\b|\bUnterstützung bieten\b|\bEntscheidung herbeiführen\b|\bMitteilung machen\b"
    r"|\bin Erwägung ziehen\b|\bBereitstellung von\b|\bseitens\b|\bzwecks\b|\bmittels\b|\bhinsichtlich\b|\bbezüglich\b"
    r"|\b\w+ung\b[^.!?]{0,40}?\b(?:durchgeführt|vorgenommen|erfolgt|erfolgen)\b"
)
CON_DE = rx(r"(?:^|[.!?]\s+)(?:Darüber hinaus|Zudem|Außerdem|Ferner|Zusätzlich|Gleichzeitig|Nicht zuletzt)\b")

# --- structure --------------------------------------------------------------------------------

OPENER_EN = rx(
    r"^\W*(?:in today'?s\b|in the (?:ever|fast)|in a world\b|ever wondered|have you ever|tired of|struggling (?:with|to)"
    r"|are you looking|welcome to\b|imagine (?:a|if)|whether you'?re|looking for (?:a|an|the)\b)"
)
OPENER_DE = rx(
    r"^\W*(?:in der heutigen|in einer welt|in einer zeit|kennst du das|kennen sie das|hast du dich schon|haben sie sich schon"
    r"|stell dir vor|stellen sie sich vor|willkommen (?:bei|auf|in)\b|egal,? ob|ob (?:du|sie|ihr)\b|suchst du|suchen sie)"
)
NXY_EN = rx(
    r"\b(?:not|n't) (?:just|only|merely|simply)\b[^.!?\n]{0,80}?\b(?:but|it'?s|they'?re|it is)\b"
    r"|\b(?:is|are)(?: not|n't) (?:just|only|merely|simply) (?:a |an |the )?\w+"
    r"|\bless (?:like )?(?:a |an )?\w+(?: \w+)? and more (?:like )?|\bit'?s not [^.!?\n]{1,60}[.,;] ?it'?s\b|\bno \w+\. no \w+\. just\b"
)
NXY_DE = rx(
    r"\bnicht nur\b[^.!?]{0,100}\bsondern(?: auch)?\b|\b(?:ist|sind|geht es um) nicht (?:einfach |nur )?[^.!?,]{1,50}[,–—]\s*(?:sondern|es ist|sie ist)\b"
    r"|\bnicht (?:nur|einfach|bloß)\b[^.!?]{1,60}[–—:]\s*(?:es|sie|er|das) ist\b|\bmehr als (?:nur )?(?:ein|eine)\b[^.!?]{0,50}[–—:,]\s*(?:es|sie|er) ist\b"
)
TRIAD = re.compile(r"(?:\b[A-ZÄÖÜ][\wäöüß-]+\.\s+){2}[A-ZÄÖÜ][\wäöüß-]+\.")
RESIDUE = rx(
    r"\b(?:i hope this helps|certainly!|of course!|great question|you'?re absolutely right|let me know if|feel free to"
    r"|i'?d be happy to|as an ai\b|here is (?:a|an|the) (?:revised|updated|draft|polished)|is there anything else"  # leak-scan: allow P04 pattern list of chatbot phrases
    r"|ich hoffe, (?:das|dies) hilft|natürlich!|sicherlich!|gerne!|absolut!|lass(?:en sie)? (?:mich|uns) wissen"
    r"|hier (?:ist|sind) (?:ein|eine|der|die|das|deine|ihre) (?:überarbeitet|aktualisiert|übersicht|version|entwurf)\w*)"
    r"|\[(?:your|company|product|name|insert|article title|firmenname|ihr name)[^\]]*\]|lorem ipsum|\{TODO[^}]*\}|\bTBD\b"
    r"|\b20\d\d-XX-XX\b|utm_source=(?:chatgpt\.com|openai|copilot\.com)|referrer=grok\.com"
)
CTA = rx(r"^\s*\[?(?:learn more|read more|click here|get started|submit|more|mehr erfahren|hier klicken|klicke hier|jetzt starten|los geht'?s|weiterlesen|mehr)\]?\s*$")
EMOJI = re.compile(r"^\s*(?:[-*•]\s*|#+\s*|\d+\.\s*)?[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705]")
TESTI = re.compile(r"^\s*>.*\s[—–]\s*[A-ZÄÖÜ][\w.]+(?: [A-ZÄÖÜ][\w.]+)*,?[^.!?]*$|[“\"„][^”\"“]{20,}[”\"“]\s*(?:[—–]\s*)?[A-ZÄÖÜ][\w.]+ [A-ZÄÖÜ][\w.]+,")

COUNT_EN = rx(r"\b(?:trusted|used|loved|chosen|relied on) by (?:over |more than |about |nearly )?\d[\d,.]*\+?\s*(?:k\b|[a-z]+)?|\b\d[\d,.]*\+? (?:teams|customers|companies|businesses|users|agencies) (?:trust|use|rely|choose)")
COUNT_DE = rx(r"\b(?:vertraut|genutzt|verwendet|gewählt) von (?:über |mehr als |rund )?\d[\d.]*\+?|\b\d[\d.]*\+? (?:Teams|Kunden|Unternehmen|Agenturen|Nutzer) (?:vertrauen|nutzen|setzen)")
SMALL_EN = {"a", "an", "the", "and", "or", "but", "for", "nor", "of", "in", "on", "at", "to", "by", "with", "from",
            "as", "vs", "via", "per", "into", "over", "up", "is", "are", "be"}
FUNC_DE = rx(r"\b(?:Und|Oder|Für|Mit|Von|Zu|Zum|Zur|Im|In|Am|Auf|Aus|Bei|Der|Die|Das|Den|Dem|Des|Ein|Eine|Einen"
             r"|Deine[nmrs]?|Dein|Ist|Sind|Wie|Was|Ohne|Über|Nach)\b", 0)
DE_COMPOUND = re.compile(r"\b(?:AI|KI|API|Cloud|Status|Server|Online|Incident|Monitoring|SaaS)\s(?:[A-ZÄÖÜ][a-zäöüß]{3,})\b")
DU = re.compile(r"\b(?:du|dich|dir|dein\w*)\b|(?:^|[.!?:]\s+)(?:Du|Dich|Dir|Dein\w*)\b")
SIE_ANY = re.compile(r"\b(?:Sie|Ihnen|Ihr\w*)\b")
DU_CAP = re.compile(r"(?<![.!?:\n]\s)(?<!^)\b(?:Du|Dich|Dir|Dein\w*)\b")

STOP_EN = set("the and is of to in that for with are this on it be as at you your we our not".split())
STOP_DE = set("der die das und ist nicht ein eine für mit von zu im auf wir du ihr sie es den dem auch wenn bei".split())


# --- text preparation -------------------------------------------------------------------------

class Doc:
    def __init__(self, text: str):
        lines = text.replace("\r\n", "\n").split("\n")
        clean = []
        in_fence = False
        in_front = bool(lines) and lines[0].strip() == "---"
        for i, line in enumerate(lines):
            if in_front:
                if i > 0 and line.strip() == "---":
                    in_front = False
                clean.append("")
                continue
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                clean.append("")
                continue
            if in_fence:
                clean.append("")
                continue
            clean.append(re.sub(r"`[^`\n]*`", " ", line))
        self.lines = clean
        self.blocks = self._blocks()
        plain = " ".join(b["text"] for b in self.blocks if not b["head"])
        self.words = len(re.findall(r"[^\W\d_]+(?:['’-][^\W\d_]+)*", re.sub(r"https?://\S+", " ", plain)))

    def _blocks(self):
        blocks, cur = [], None

        def flush():
            nonlocal cur
            if cur:
                blocks.append(cur)
            cur = None

        for n, line in enumerate(self.lines, 1):
            if not line.strip():
                flush()
                continue
            head = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line)
            if head:
                flush()
                blocks.append({"line": n, "text": head.group(1).strip(), "head": True, "offs": [0]})
                continue
            if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line) or line.lstrip().startswith("|") or line.lstrip().startswith(">"):
                flush()
            if cur is None:
                cur = {"line": n, "text": line.strip(), "head": False, "offs": [0]}
            else:
                cur["offs"].append(len(cur["text"]) + 1)
                cur["text"] += " " + line.strip()
        flush()
        return blocks


def line_of(block, offset):
    idx = 0
    for k, o in enumerate(block["offs"]):
        if o <= offset:
            idx = k
    return block["line"] + idx


def sentences(block):
    out, start = [], 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ\"„(\[])", block["text"]):
        out.append((start, block["text"][start:m.start()]))
        start = m.end()
    out.append((start, block["text"][start:]))
    return [(line_of(block, s), t) for s, t in out if t.strip()]


def detect_lang(text: str) -> str:
    toks = re.findall(r"[a-zäöüß]+", text.lower())
    en = sum(1 for t in toks if t in STOP_EN)
    de = sum(1 for t in toks if t in STOP_DE)
    return "de" if de > en else "en"


# --- the checks ---------------------------------------------------------------------------------

def lint_text(text: str, lang: str, glossary=None):
    if lang == "auto":
        lang = detect_lang(text)
    doc = Doc(text)
    out = []  # (line, code, message)

    def add(line, code, msg):
        out.append((line, code, msg))

    de = lang == "de"
    words = max(doc.words, 1)
    src, mech = (SRC_DE, MECH_DE) if de else (SRC_EN, MECH_EN)
    sup, clm = (SUP_DE, CLM_DE) if de else (SUP_EN, CLM_EN)

    sents = []
    for b in doc.blocks:
        for ln, s in sentences(b):
            sents.append((ln, s, b["head"]))

    # SUP01 and CLM01 work per sentence
    for ln, s, head in sents:
        for m in sup.finditer(s):
            rest = s[:m.start()] + " " + s[m.end():]
            if not src.search(rest):
                add(ln, "SUP01", f"'{m.group(0).strip()}' has no source marker (number, link, 'laut', 'according to') in the sentence")
                break
        if not head and clm.search(s) and not re.search(r"\d", s) and not mech.search(s):
            m = clm.search(s)
            add(ln, "CLM01", f"'{m.group(0)}' without a number, unit or mechanism")

    # tell lists
    soft_hits = []
    for b in doc.blocks:
        t = b["text"]
        if not de:
            for m in TEL_EN_CORE.finditer(t):
                add(line_of(b, m.start()), "TEL01", f"core tell word '{m.group(0)}'")
            for m in TEL_EN_SOFT.finditer(t):
                if b["head"]:
                    add(b["line"], "TEL02", f"soft tell word '{m.group(0)}' in a heading")
                else:
                    soft_hits.append((line_of(b, m.start()), m.group(0)))
            for m in TEL_EN_MKT.finditer(t):
                add(line_of(b, m.start()), "TEL03", f"marketing filler '{m.group(0)}': name the proof or delete")
            for pat, label in TEL_EN_PHRASE:
                for m in pat.finditer(t):
                    add(line_of(b, m.start()), "TEL04", f"{label}: '{m.group(0).strip()}'")
        else:
            for pat, label in TEL_DE_PHRASE:
                for m in pat.finditer(t):
                    add(line_of(b, m.start()), "TEL04", f"{label}: '{m.group(0).strip()}'")
    allowed = max(1, words // 500)
    if len(soft_hits) > allowed:
        ln, w = soft_hits[allowed]
        add(ln, "TEL02", f"{len(soft_hits)} soft tell words ({', '.join(sorted({h[1].lower() for h in soft_hits}))}); "
                         f"more than {allowed} per {words} words")

    # transitions (EN) and connectors (DE): density
    conn = TRANSITION_EN if not de else CON_DE
    hits = [(line_of(b, m.start()), m.group(0).strip(" .!?")) for b in doc.blocks if not b["head"] for m in conn.finditer(b["text"])]
    limit = max(1, words // (150 if de else 300))
    if len(hits) > limit:
        add(hits[limit][0], "CON01", f"{len(hits)} sentence-initial connectors in {words} words")

    # opener
    body = [b for b in doc.blocks if not b["head"]]
    if body:
        first = body[0]["text"][:250]
        m = (OPENER_DE if de else OPENER_EN).search(first)
        if m:
            add(body[0]["line"], "OPN01", f"generic opener '{m.group(0).strip()}': the first sentence should say what it does")

    # contrast
    nxy = NXY_DE if de else NXY_EN
    nhits = []
    for i, b in enumerate(doc.blocks):
        for m in nxy.finditer(b["text"]):
            nhits.append((line_of(b, m.start()), b["head"] or (b is body[0] if body else False) and m.start() < 200))
    cap = max(1, words // 400)
    if len(nhits) > cap:
        add(nhits[cap][0], "NXY01", f"{len(nhits)} 'not X but Y' contrasts in {words} words; keep a contrast only if readers hold the rejected view")
    elif nhits and any(h[1] for h in nhits):
        add(next(h[0] for h in nhits if h[1]), "NXY01", "'not X but Y' contrast in a heading or the first sentence")

    for b in doc.blocks:
        for m in TRIAD.finditer(b["text"]):
            add(line_of(b, m.start()), "TRI01", f"staccato triad '{m.group(0)}': one claim with proof beats three adjectives")

    # dashes
    text_all = "\n".join(b["text"] for b in doc.blocks)
    em = text_all.count("—")
    if de:
        for b in doc.blocks:
            for m in re.finditer("—", b["text"]):
                add(line_of(b, m.start()), "DSH01", "em dash in German text: use a period, colon or the spaced en dash")
            for m in re.finditer(r"\s[–—]\s[^.!?\n]{1,160}?\s[–—][\s,]", b["text"]):
                add(line_of(b, m.start()), "DSH03", "paired dash insertion: write the aside as its own sentence")
    elif em >= 2 and em * 1000 / words > 2:
        add(next(b["line"] for b in doc.blocks if "—" in b["text"]), "DSH01", f"{em} em dashes in {words} words (more than 2 per 1,000)")
    for b in doc.blocks:
        for m in re.finditer(r"[–—]\s*,", b["text"]):
            add(line_of(b, m.start()), "DSH02", "dash followed by a comma reads as broken: rebuild the sentence")

    # headings
    for b in doc.blocks:
        if not b["head"]:
            continue
        if de:
            m = None
            ws = b["text"].split()
            if len(ws) > 2:
                m = FUNC_DE.search(" ".join(ws[1:]))
            if m:
                add(b["line"], "TTL01", f"heading looks like English title case ('{m.group(0)}' is capitalised): German headings capitalise nouns only")
        else:
            ws = re.findall(r"[A-Za-z][A-Za-z'’-]*", re.sub(r"\*\*|__", "", b["text"]))
            rest = [w for w in ws[1:] if w.lower() not in SMALL_EN]
            if len(ws) >= 3 and len(rest) >= 2 and sum(1 for w in rest if w[0].isupper()) / len(rest) >= 0.8:
                add(b["line"], "TTL01", "title-case heading: use sentence case (proper nouns and product names excepted)")

    # residue, emoji, exclamation, CTA, testimonials
    excl = 0
    for n, line in enumerate(doc.lines, 1):
        if not line.strip():
            continue
        m = RESIDUE.search(line)
        if m:
            add(n, "RES01", f"chat residue or placeholder '{m.group(0)}'")
        if EMOJI.match(line):
            add(n, "EMO01", "emoji at the start of a heading, list item or paragraph")
        cm = (COUNT_DE if de else COUNT_EN).search(line)
        if cm:
            add(n, "CNT01", f"customer or user count '{cm.group(0).strip()}': needs a dated source record")
        if CTA.match(line):
            add(n, "CTA01", "generic label: name the action and its object")
        if TESTI.search(line):
            add(n, "TST01", "testimonial: needs a consent and source record; the linter cannot verify it exists")
        excl += len(re.findall(r"!(?=\s|$)", line))
    if excl > 1:
        add(1, "EXC01", f"{excl} exclamation marks; at most one per marketing page, none in docs or notices")

    # calques and register notes (both languages)
    for b in doc.blocks:
        for pat, alt, ratio in (CAL_DE if de else CAL_EN):
            for m in pat.finditer(b["text"]):
                add(line_of(b, m.start()), "CAL01", f"calque or unidiomatic '{m.group(0)}': natural form {alt} (corpus {ratio})")
        for pat, note in (CAL_DE_NOTE if de else CAL_EN_NOTE):
            for m in pat.finditer(b["text"]):
                add(line_of(b, m.start()), "CAL02", f"register: {note}")

    # product glossary
    for row in glossary or []:
        if row["lang"] not in ("*", lang):
            continue
        for b in doc.blocks:
            for pat, variant in row["avoid"]:
                for m in pat.finditer(b["text"]):
                    add(line_of(b, m.start()), "GLO01", f"'{m.group(0)}' is not the house term: use '{row['preferred']}' (glossary)")

    # sentence length
    long_ = [(ln, len(re.findall(r"\w+", s))) for ln, s, head in sents if not head]
    counted = [x for x in long_ if x[1] >= 4]
    over = [x for x in counted if x[1] > 25]
    if len(counted) >= 4 and len(over) / len(counted) > 0.15:
        add(over[0][0], "LEN01", f"{len(over)} of {len(counted)} sentences have more than 25 words")

    if de:
        for b in doc.blocks:
            t = b["text"]
            for m in re.finditer(r"(?:^|[\s(\[])“|”", t):
                add(line_of(b, m.start()), "TYP01", "English quotes: German uses „…“ or »…«")
            for m in re.finditer(r"(?<![=\w])\"[A-Za-zÄÖÜäöü][^\"\n]{0,80}\"", t):
                add(line_of(b, m.start()), "TYP01", "straight quotes in German prose: use „…“")
            for m in re.finditer(r"\b[A-ZÄÖÜ][\wäöüß]*['’]s\b", t):
                add(line_of(b, m.start()), "TYP02", f"apostrophe before -s ('{m.group(0)}'); check the proper-name exception")
            for m in DE_COMPOUND.finditer(t):
                add(line_of(b, m.start()), "TYP03", f"split compound '{m.group(0)}': write one word or hyphenate")
            for m in re.finditer(r"[?!…](?:\*\*|“|\")?[,.;:]", t):
                add(line_of(b, m.start()), "TYP04", "punctuation directly after a label ending in ? ! …: rebuild the sentence")
            for m in re.finditer(r"€\s?\d|\d€|\b[1-9]\d{0,2},\d{3}\b(?![,\d])|€\.", t):
                add(line_of(b, m.start()), "TYP05", f"number or currency format '{m.group(0)}': German writes '19 €' and '1.000'")
            for m in FVG_DE.finditer(t):
                add(line_of(b, m.start()), "FVG01", f"nominal or official style '{m.group(0)}': use a verb")
            for m in ([] if b["head"] else DU_CAP.finditer(t)):
                add(line_of(b, m.start()), "ADR02", "capitalised Du/Dein mid-sentence: du and dein are lowercase outside letters")
        du = sum(len(DU.findall(b["text"])) for b in doc.blocks)
        sie = 0
        for b in doc.blocks:
            for m in SIE_ANY.finditer(b["text"]):
                before = b["text"][:m.start()].rstrip()
                if m.group(0) == "Sie" and (not before or before[-1] in ".!?:\"„»*#-"):
                    continue
                if m.group(0).startswith("Ihr") and (not before or before[-1] in ".!?:\"„»*#-"):
                    continue
                sie += 1
        if du and sie:
            add(1, "ADR01", f"du ({du}) and Sie ({sie}) both used: decide one address form per product")
    return lang, sorted(out)


# --- product voice files ------------------------------------------------------------------------

def load_glossary(path: str):
    """Read a glossary table: | lang | preferred | avoid | note |. 'avoid' holds comma-separated literal
    variants; a trailing * matches any word ending. Rows whose lang is not de, en or * are skipped."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or cells[0].lower() not in ("de", "en", "*"):
                continue
            avoid = []
            for v in (x.strip().strip("`") for x in cells[2].split(",")):
                if not v or v in ("-", "–"):
                    continue
                body = re.escape(v[:-1]) + r"\w*" if v.endswith("*") else re.escape(v)
                avoid.append((re.compile(r"(?<![\w-])" + body + r"(?![\w-])", re.IGNORECASE), v))
            if avoid:
                rows.append({"lang": cells[0].lower(), "preferred": cells[1].strip("`"), "avoid": avoid})
    return rows


REQUIRED_CORRECTION_KEYS = ("date", "surface", "lang", "before", "after", "reason")
PERSONAL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|(?<!\d)(?:\+|00)\d[\d ()/-]{7,}\d")


def voice_check(root: str):
    """Check a voice directory. Returns a list of (file, line, code, message)."""
    out = []
    for name in ("voice.md", "glossary.md", "corrections.jsonl"):
        if not os.path.isfile(os.path.join(root, name)):
            out.append((name, 0, "VOI03", "missing; start from the skill's assets/voice/ templates"))
    ex = os.path.join(root, "examples")
    shipped = [f for f in (os.listdir(ex) if os.path.isdir(ex) else []) if f.endswith(".md") and not f.startswith("_")]
    if not shipped:
        out.append(("examples/", 0, "VOI03", "no approved examples: drafts stay marked as unreviewed voice"))
    path = os.path.join(root, "corrections.jsonl")
    if not os.path.isfile(path):
        return out
    seen = {}
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except ValueError as e:
                out.append(("corrections.jsonl", n, "VOI01", f"not valid JSON: {e}"))
                continue
            if not isinstance(rec, dict):
                out.append(("corrections.jsonl", n, "VOI01", "each line must be a JSON object"))
                continue
            if rec.get("_template"):
                continue  # the format line shipped with the template
            missing = [k for k in REQUIRED_CORRECTION_KEYS if not str(rec.get(k, "")).strip()]
            if missing:
                out.append(("corrections.jsonl", n, "VOI01", f"missing {', '.join(missing)}"))
            if rec.get("date") and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(rec["date"])):
                out.append(("corrections.jsonl", n, "VOI01", "date must be YYYY-MM-DD"))
            if rec.get("lang") and rec["lang"] not in ("de", "en"):
                out.append(("corrections.jsonl", n, "VOI01", "lang must be de or en"))
            if PERSONAL.search(" ".join(str(rec.get(k, "")) for k in ("before", "after", "reason"))):
                out.append(("corrections.jsonl", n, "VOI04", "email address or phone number: store the pattern, not personal data"))
            rule = str(rec.get("rule", "")).strip().lower()
            if rule:
                entry = seen.setdefault(rule, {"lines": [], "promoted": False})
                entry["lines"].append(n)
                entry["promoted"] = entry["promoted"] or bool(str(rec.get("promoted", "")).strip())
    for rule, entry in sorted(seen.items()):
        if len(entry["lines"]) >= 2 and not entry["promoted"]:
            out.append(("corrections.jsonl", entry["lines"][-1], "VOI02",
                        f"rule '{rule}' corrected {len(entry['lines'])} times and not promoted: add a glossary row or "
                        f"a lint rule, then set 'promoted' on the entry"))
    return out


# --- self-test ----------------------------------------------------------------------------------

GOOD_EN = """# Move a booking

You can now move a booking to another slot. The guest gets an email with the new time, and the old slot opens again.

Reminders go out 24 hours before each appointment, by email or text message. Free accounts have 60 API requests per minute, Team accounts 600.

The median reminder reached the guest in 11 seconds in our 2026 audit (source: https://example.com/audit).

```
robust seamless cutting-edge
```
"""

BAD_EN = """# Our Powerful Booking Management Platform

In today's fast-paced digital world, scheduling is not just a tool. It's peace of mind. We are the best booking platform on the market — seamless, robust, and effortless — and our cutting-edge solution unlocks the power of your team — ensuring a seamless experience for everyone. This release marks a pivotal milestone in our journey. Experts agree that reminders matter because guests forget. Move faster without compromising security! Great!

It's not just alerting. It's confidence.
"""

GOOD_DE = """# Rechnungen schreiben und verschicken

Du legst eine Rechnung an, wählst den Kunden und trägst die Positionen ein. Die Rechnung geht als PDF per E-Mail raus, mit deinem Logo und deiner Bankverbindung. Zahlt der Kunde nicht, erinnern wir ihn nach 14 Tagen.

Das kostet 19 € im Monat. Alle Preise netto. Laut unserer Auswertung vom Oktober 2026 dauert eine Rechnung im Median 90 Sekunden.
"""

BAD_DE = """# Schnelle Und Einfache Rechnungen Für Deine Kunden

In der heutigen schnelllebigen Welt ist eine gute Buchhaltung nicht nur ein Nice-to-have — es ist ein echter Gamechanger. Egal ob Startup oder Enterprise: Unsere ganzheitliche Plattform bietet Ihnen eine nahtlose Integration in deine bestehenden Workflows. Tauche ein in eine Welt, in der offene Posten der Vergangenheit angehören. Darüber hinaus wird durch die Bereitstellung von maßgeschneiderten Vorlagen ein echter Mehrwert für Ihr Team geschaffen. Wir sind die beste Rechnungssoftware am Markt. Die "Online Rechnung" zeigt Kunden's Zahlungen. Das kostet €19 pro Monat. In 2026 haben wir viele Probleme adressiert. Natürlich! Hier ist eine Übersicht.
"""

EXPECT_BAD_EN = {"OPN01", "TTL01", "NXY01", "SUP01", "TEL01", "TEL02", "TEL03", "TEL04", "DSH01", "EXC01", "CLM01"}
EXPECT_BAD_DE = {"OPN01", "TTL01", "NXY01", "DSH01", "SUP01", "TEL04", "ADR01", "TYP01", "TYP02", "TYP03", "TYP05",
                 "RES01", "FVG01", "CAL01"}


def self_test() -> int:
    fails = []

    def codes(text, lang):
        return {c for _, c, _ in lint_text(text, lang)[1]}

    got = lint_text(GOOD_EN, "en")[1]
    if got:
        fails.append(f"good EN text produced warnings: {got}")
    got = lint_text(GOOD_DE, "de")[1]
    if got:
        fails.append(f"good DE text produced warnings: {got}")
    miss = EXPECT_BAD_EN - codes(BAD_EN, "en")
    if miss:
        fails.append(f"bad EN text did not trigger {sorted(miss)}")
    miss = EXPECT_BAD_DE - codes(BAD_DE, "de")
    if miss:
        fails.append(f"bad DE text did not trigger {sorted(miss)}")
    if "TST01" not in codes("> It cut our setup time in half and we never looked back.\n> — Sarah Miller, Acme", "en"):
        fails.append("testimonial block not flagged")
    if lint_text(BAD_EN, "auto")[0] != "en" or lint_text(BAD_DE, "auto")[0] != "de":
        fails.append("language detection failed")
    if "SUP01" not in codes("We are the fastest booking tool.", "en"):
        fails.append("unsourced EN superlative not flagged")
    if "SUP01" in codes("The fastest reminder we measured among five tools took 30 seconds (benchmark, 2026-10).", "en"):
        fails.append("sourced EN superlative flagged")
    if "SUP01" not in codes("Wir sind die schnellste Buchungssoftware.", "de"):
        fails.append("unsourced DE superlative not flagged")
    if "SUP01" not in codes("Trusted by 10,000 teams, we are the fastest booking tool.", "en"):
        fails.append("a bare digit must not count as a source")
    if "CNT01" not in codes("Trusted by over 10,000 teams worldwide.", "en"):
        fails.append("customer count not flagged")
    if "TST01" not in codes('"It cut our invoicing time in half." Sarah Miller, Operations Lead', "en"):
        fails.append("inline testimonial not flagged")
    if "SUP01" in codes("Laut Umfrage 2026 ist es die schnellste Buchungssoftware.", "de"):
        fails.append("sourced DE superlative flagged")
    if "SUP01" in codes("Follow best practices and read the first step.", "en"):
        fails.append("false positive on 'best practices' or 'first step'")
    if "DSH02" not in codes("Wer PHP nutzt — etwa für Kunden —, braucht kein JSON.", "de"):
        fails.append("dash plus comma not flagged")
    # calques: real ones flagged, established ones left alone
    for text in ("Wir müssen eine Entscheidung machen.", "Die Funktion ist nicht länger verfügbar.",
                 "Wir sind so aufgeregt über das Update.", "Teile dein Feedback mit uns."):
        if "CAL01" not in codes(text, "de"):
            fails.append(f"DE calque not flagged: {text}")
    for text in ("Das Projekt läuft einmal mehr nach Plan.", "Der Brief ist adressiert an die Buchhaltung.",
                 "Wir treffen eine Entscheidung."):
        if "CAL01" in codes(text, "de"):
            fails.append(f"established DE phrase flagged as calque: {text}")
    if codes("Das macht Sinn.", "de") & {"CAL01"} or "CAL02" not in codes("Das macht Sinn.", "de"):
        fails.append("'macht Sinn' must be a register note (CAL02), not a calque")
    for text in ("We use the tool since three years.", "You will become an email with the link.",
                 "Please explain me the invoice.", "We look forward to hear from you."):
        if "CAL01" not in codes(text, "en"):
            fails.append(f"EN calque not flagged: {text}")
    if "TEL04" not in codes("Ups! Das hat nicht geklappt.", "de") or "TEL04" not in codes("Oops, something broke.", "en"):
        fails.append("UI joke or apology not flagged")
    if "FVG01" not in codes("Die Speicherung konnte nicht durchgeführt werden.", "de"):
        fails.append("noun plus 'durchgeführt' not flagged")
    if "CAL01" in codes("We have used it for three years and take a photo of each receipt.", "en"):
        fails.append("idiomatic EN flagged as calque")
    # glossary and voice files
    tmp = tempfile.mkdtemp(prefix="copy-lint-")
    gl = os.path.join(tmp, "glossary.md")
    with open(gl, "w", encoding="utf-8") as fh:
        fh.write("| lang | preferred | avoid | note |\n|---|---|---|---|\n"
                 "| de | Termin | Slot*, Zeitfenster | Buchungen |\n| en | booking | reservation | |\n")
    g = load_glossary(gl)
    if "GLO01" not in {c for _, c, _ in lint_text("Wähle einen freien Slot.", "de", g)[1]}:
        fails.append("glossary variant with * not flagged")
    if {c for _, c, _ in lint_text("Wähle einen freien Termin.", "de", g)[1]} & {"GLO01"}:
        fails.append("preferred glossary term flagged")
    if {c for _, c, _ in lint_text("Your reservation is confirmed.", "de", g)[1]} & {"GLO01"}:
        fails.append("EN glossary row applied to German text")
    with open(os.path.join(tmp, "corrections.jsonl"), "w", encoding="utf-8") as fh:
        rec = {"date": "2026-11-03", "surface": "ui-error", "lang": "de", "before": "Ein Fehler ist aufgetreten.",
               "after": "Die Rechnung wurde nicht gespeichert.", "reason": "say what failed", "rule": "name what failed"}
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.write(json.dumps(dict(rec, before="Fehler beim Speichern", after="Projekt nicht gespeichert"), ensure_ascii=False) + "\n")
        fh.write(json.dumps(dict(rec, before="Mail an anna@example.com fehlgeschlagen", rule=""), ensure_ascii=False) + "\n")
        fh.write("{not json\n")
    vc = {c for _, _, c, _ in voice_check(tmp)}
    shutil.rmtree(tmp, ignore_errors=True)
    for want in ("VOI01", "VOI02", "VOI03", "VOI04"):
        if want not in vc:
            fails.append(f"voice check did not report {want}")
    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("copy_lint self-test: ok (good EN/DE clean, bad EN/DE flagged, calques, glossary, voice files, "
          "32 spot checks)")
    return 0


# --- command line --------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="copy_lint.py",
        description="Flag unsourced superlatives, tell phrases, calques, dash and contrast density and typography "
                    "faults in English or German copy, plus product glossary variants. Warnings only; --strict makes "
                    "them fail.",
    )
    ap.add_argument("files", nargs="*", help="files to check; - reads stdin")
    ap.add_argument("--lang", choices=["en", "de", "auto"], default="auto", help="text language (default: auto)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any warning is printed")
    ap.add_argument("--glossary", metavar="FILE", help="product glossary table (lang | preferred | avoid | note); "
                    "flags forbidden variants as GLO01")
    ap.add_argument("--voice-check", metavar="DIR", help="check a voice directory (voice.md, glossary.md, "
                    "corrections.jsonl, examples/) and exit")
    ap.add_argument("--self-test", action="store_true", help="run the built-in good and bad texts and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.voice_check:
        if not os.path.isdir(args.voice_check):
            print(f"copy_lint.py: {args.voice_check} is not a directory", file=sys.stderr)
            return 2
        found = voice_check(args.voice_check)
        for f, ln, code, msg in found:
            print(f"{os.path.join(args.voice_check, f)}:{ln}: WARN {code} {msg}")
        print(f"{len(found)} voice warning(s)", file=sys.stderr)
        return 1 if (args.strict and found) else 0
    glossary = None
    if args.glossary:
        try:
            glossary = load_glossary(args.glossary)
        except (OSError, UnicodeDecodeError) as e:
            print(f"copy_lint.py: cannot read glossary {args.glossary}: {e}", file=sys.stderr)
            return 2
    if not args.files:
        ap.print_usage(sys.stderr)
        print("copy_lint.py: no input; give a file, - for stdin, or --self-test", file=sys.stderr)
        return 2

    total = 0
    for name in args.files:
        try:
            text = sys.stdin.read() if name == "-" else open(name, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"copy_lint.py: cannot read {name}: {e}", file=sys.stderr)
            return 2
        lang, found = lint_text(text, args.lang, glossary)
        label = "stdin" if name == "-" else name
        for ln, code, msg in found:
            print(f"{label}:{ln}: WARN {code} [{lang}] {msg}")
        total += len(found)
    print(f"{total} warning(s); word lists last reviewed {WORDLIST_REVIEWED}", file=sys.stderr)
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
