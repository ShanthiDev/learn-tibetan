# Deutsche Lautumschrift (TZ-Stil): Methodik, Evidenz und aktueller Stand

**Created:** 2026-09-25T17:05:16+02:00
**Last updated:** 2026-09-25T19:01:52+02:00
**Status:** superseded (2026-09-25T19:01:52+02:00) by `docs/tz-umschrift.md`. Dieses Dokument bleibt als Stand der Planungsphase erhalten; die Mantra-Behandlung, die Varianten und die Integration wurden danach geändert.
**Origin:** repository_agent_generated
**Document role:** research_report
**Ergänzt:** `docs/research/phonetics-01-tz-generator-exploration.md`, den technischen Bericht
mit allen Zahlen. Das vorliegende Dokument erklärt denselben Stand für Leser ohne
Tibetischkenntnisse.

---

## 1. Worum es geht

Der Reader soll zu jeder tibetischen Passage eine deutsch lesbare Aussprachehilfe anbieten, und
zwar in der Schreibweise des Tibetischen Zentrums (TZ). Ein Beispiel: `sang gyä tschö dang tsog gyi
tschog nam la`. Bisher enthält der Reader nur sechs von Hand geschriebene Beispiele.

Das Dokument beantwortet drei Fragen:

1. Wie funktioniert der jetzt gebaute Generator?
2. Woher wissen wir, dass er brauchbar ist? Welche Evidenz haben wir, und wie wurde geprüft?
3. Was ist gebaut, was nicht, und welche Entscheidungen stehen an?

---

## 2. Wie der Generator funktioniert

### 2.1 Grundidee: Regeln statt einer großen Tabelle

Die tibetische Schrift ist sehr regelmäßig. Jede Silbe wird zwischen zwei Silbenpunkten (་)
geschrieben und hat einen festen Aufbau aus bis zu sieben Positionen:

| Position | Beispiel in བསྒྲུབས (ausgesprochen *drub*) | Wirkung auf die Aussprache |
|---|---|---|
| Vorsilbe (Präfix) | བ | stumm |
| Aufgesetzter Buchstabe | ས | stumm |
| **Grundbuchstabe** | ག | bestimmt den Anlaut |
| Untergesetzter Buchstabe | ར | verändert den Anlaut: ག + ར → *dr* |
| Vokal | ུ | *u* |
| Endbuchstabe | བ | *b* |
| Zweiter Endbuchstabe | ས | stumm |

Der Generator zerlegt jede Silbe in diese Positionen und setzt die Aussprache aus kleinen Tabellen
zusammen. Er hat also **keine große Zuordnungstabelle Silbe → Umschrift**, sondern eine Handvoll
kleiner Regeltabellen:

| Tabelle | Größe | Beispiele |
|---|---:|---|
| Grundbuchstabe → Anlaut | 30 | ཅ/ཆ → *tsch*, ཇ → *dsch*, ཞ/ཤ → *sch*, ཚ → *tsh* |
| Untergesetztes ཡ | 8 | ཕྱ → *tsch*, བྱ → *dsch*, ཀྱ → *ky* |
| Untergesetztes ར | 14 | ཀྲ → *tr*, ཁྲ → *thr*, གྲ → *dr* |
| Untergesetztes ལ | 6 | གླ → *l*, ཟླ → *d* |
| Endbuchstaben | 10 | ག → *g*, ང → *ng*, ད/ས → stumm |
| Umlautregel | 1 Regel | nach ད ས ན ལ und beim Genitiv འི: a → ä, o → ö, u → ü |

Dazu kommen einige Sonderregeln, zum Beispiel དབ → *w* (དབང *wang*) und angehängte Partikeln
(པའི *pä*).

Der Vorteil: Die Regeln funktionieren auch für Silben, die in keiner TZ-Quelle vorkommen. Deshalb
gibt es im gesamten Hayagrīva-Text keine einzige Silbe ohne Vorschlag.

### 2.2 Sanskrit und Mantras

Mantras (OM, HUNG, BENDSA …) folgen nicht den tibetischen Regeln. Der Generator hat dafür zwei
Hilfsmittel:

- ein **kleines Mantra-Lexikon** mit etwa 50 Einträgen für feste TZ-Schreibungen wie བཛྲ → *BENDSA*,
  སྭཱཧཱ → *SOHA*, པདྨ → *PEMA*, ཕཊ → *PHE*;
- eine **Sanskrit-Umschrift** für alles andere, zum Beispiel མཧཱ → *MAHA*, སིདྡྷི → *SIDDHI*.

Ob eine Silbe Sanskrit ist, erkennt er an Zeichen, die im Tibetischen nicht vorkommen (lange Vokale,
ཾ, ཿ, retroflexe Buchstaben), und an unmöglichen Buchstabenkombinationen. Besteht eine Phrase
überwiegend aus Sanskrit, schreibt er sie in GROSSBUCHSTABEN wie TZ.

### 2.3 Wo das Mapping des anderen Agenten ins Spiel kommt

Das externe Mapping enthält 822 Silben mit den Schreibungen, die in zwei TZ-Heften beobachtet
wurden. Der Generator nutzt diese Schreibungen **als Kontrolle**, nicht als Hauptquelle:

- **Regel und TZ-Beleg stimmen überein** (Status *confirmed*): Die Regel wird genommen. Das betrifft
  zwei Drittel aller Silben im Hayagrīva-Text.
- **TZ-Beleg widerspricht der Regel mindestens zweimal und hat die Mehrheit:** Der Beleg gewinnt.
  Das kam nur bei 4 Silben vor, etwa རྡོ → *dor* (wie in *dor dsche*), wo die reine Regel *do*
  ergeben würde.
- **Nur ein einzelner widersprechender Beleg:** Die Regel wird genommen und der Fall markiert, weil
  einzelne Belege oft Erkennungs- oder Zuordnungsfehler sind.

### 2.4 Umschaltbare Konventionen

Nach allen Regeln wird eine Konvention angewendet. Das ist eine reine Schreib-Umformung am
Silbenanfang:

| Konvention | Quelle | Behauchung | ཛ | Beispiel ཚོགས / ཐམས / ཕན |
|---|---|---|---|---|
| `hayagriva` (derzeit Standard) | TZ-Hayagrīva-Heft 2023 | markiert (*tsh, th, kh, ph*) | *dz* | *tshog / tham / phän* |
| `gebetsbuch` | TZ-Gebetsbuch (lange in Gebrauch) | nicht markiert | *ds* | *tsog / tam / pän* |

### 2.5 Ablauf für eine Passage

1. Den tibetischen Text an den Satzzeichen (།) in Phrasen teilen. Zeilenumbrüche sind nur Layout
   und trennen nichts.
2. Jede Phrase an den Silbenpunkten (་) in Silben teilen.
3. Pro Silbe in dieser Reihenfolge prüfen: manuelle Korrektur (zurzeit leer) → Mantra-Lexikon →
   Regel plus TZ-Beleg → reine Regel → Sanskrit-Umschrift.
4. Die Konvention anwenden. Überwiegend aus Sanskrit bestehende Phrasen großschreiben.
5. Für jede Silbe festhalten, **woher** ihr Wert kommt: *confirmed*, *rule_tibetan*,
   *mantra_exception* usw.

Beispiel: ༄༅། །པདྨ་ཡང་གསང་ཁྲོས་པའི་ལས་བྱང་… ergibt
*pema yang sang thrö pä lä dschang nying po tschü dü*.

---

## 3. Evidenz und Prüfmethodik

Die Prüfung ruht auf **drei voneinander unabhängigen Quellen**. Wo sie übereinstimmen, ist das
Ergebnis belastbar.

| Quelle | Was sie ist | Grenzen |
|---|---|---|
| **A. Regelwissen** | Die tibetischen Rechtschreib- und Ausspracheregeln, aus dem Trainingswissen des Assistenten in Code gegossen | Von keinem Menschen geprüft |
| **B. TZ-Beobachtungen** | Die 1.427 Zuordnungen „tibetische Silbe ↔ gedruckte TZ-Umschrift“ aus zwei TZ-Heften, extrahiert vom anderen Agenten | Durch dessen Texterkennung fehlerbehaftet |
| **C. Die Original-PDFs** | TZ-Hayagrīva-Heft, TZ-Chakrasamvara-Sādhana, TZ-Gebetsbuch; vom Assistenten lokal mit Tesseract neu erkannt | Scans; auch Tesseract macht Fehler |

### 3.1 Prüfung 1: Regeln gegen TZ-Beobachtungen (A gegen B)

- **Vorgehen:** Für jede beobachtete Silbe erzeugen die Regeln einen Wert, und der wird mit der
  gedruckten TZ-Schreibung verglichen. Konventionsunterschiede (*tsh/z*, *th/t*) gelten dabei nicht
  als Fehler.
- **Ergebnis:** 488 von 544 vergleichbaren Silben stimmen überein, also 89,7 %.
- **Einschränkung:** Einige Regeln wurden beim Hinsehen auf genau diese Daten nachgeschärft. Die
  Zahl ist deshalb etwas geschönt; unabhängig misst erst Prüfung 3.
- **Nebenergebnis:** Bei den restlichen Silben ließen sich im Mapping des anderen Agenten
  wiederkehrende Fehlermuster erkennen. Beispiele: Umlautpunkte verloren (*pa* statt *pä*),
  Zeichensalat (*gyda*, *nd*), falsch zugeordnete Silben (ཐོ → *tschig*), und die feste Bevorzugung
  eines Heftes selbst gegen klare Mehrheiten. Diese Diagnosen waren zunächst **Schlussfolgerungen**,
  keine geprüften Tatsachen.

### 3.2 Prüfung 2: Neu erkannte Originalseiten gegen TZ-Beobachtungen (C gegen B)

- **Vorgehen:** Alle 105 Seiten wurden lokal mit Tesseract erkannt. Die lokale Erkennung kostet
  keine Modell-Tokens. Ein Skript legt pro Seite die Umschrift-Wörter des anderen Agenten neben die
  eigene Erkennung.
- **Ergebnis:** 1.092 von 1.163 zuordenbaren Beobachtungen sind identisch (93,9 %). Von den 71
  Abweichungen sind 35 verlorene Umlaute beim anderen Agenten; die meisten übrigen sind sein
  Zeichensalat.
- **Was damit am Druck belegt ist:** die Umlautverluste und der Zeichensalat aus Prüfung 1.
- **Was sich als falsch herausstellte:**
  - *Iha* ist kein Lesefehler des anderen Agenten. Im Druckfont sehen l und I gleich aus.
  - TZ ist nicht innerhalb eines Heftes einheitlich. Das Hayagrīva-Heft druckt sowohl *tshog* als
    auch *zog*, *scho* als auch *schog*, *pal* als auch *päl*.
- **Bewertung der Arbeit des anderen Agenten:** Die Datenerhebung ist solide. Die Zusammenführung
  zu einem Endwert und die aus Regeln abgeleiteten Einträge sind es nicht.

### 3.3 Prüfung 3: Unabhängiger Test am Gebetsbuch (A gegen C)

- **Warum dieser Test entscheidend ist:** Das Gebetsbuch wurde beim Bau der Regeln nicht verwendet.
  Es misst also, wie gut der Generator auf Material funktioniert, das er nicht kennt.
- **Problem:** Das Gebetsbuch druckt kein Tibetisch.
- **Lösung:** Viele Texte darin sind bekannte Standardgebete. Für 64 Zeilen (Zuflucht, Wunschgebet
  für gutes Verhalten, Mandala, Beichte) hat der Assistent den tibetischen Originaltext **aus dem
  Gedächtnis** aufgeschrieben. Den hat der Generator umgeschrieben, und das Ergebnis wurde Wort für
  Wort mit der gedruckten TZ-Umschrift verglichen.
- **Ergebnis:**

  | Konvention | identische Silben |
  |---|---:|
  | `gebetsbuch` | **551 von 566 (97,3 %)** |
  | `hayagriva` | 522 von 566 (92,2 %); die Differenz ist fast nur die Behauchung |

- **Art der Abweichungen:** Es gab **keine falsche Silbe.** Die 15 Abweichungen sind Feinheiten:
  - Genitiv nach u/o ohne Umlaut (*tschu* statt *tschü*);
  - ཅི als *tschi* statt *dschi*;
  - Lautverschleifungen (*nab sa*);
  - je ein Erkennungsfehler und ein möglicher Fehler in der Rekonstruktion.
- **Mapping ohne Einfluss:** Mit und ohne das Mapping des anderen Agenten kommt dasselbe heraus.
- **Einschränkungen:** Die tibetischen Testzeilen sind nicht geprüft; ein Rekonstruktionsfehler
  zählt gegen den Generator. Mantras kamen in diesem Test nicht vor.

### 3.4 Wie hoch ist das Vertrauen?

| Bereich | Anteil am Hayagrīva-Text | Vertrauen | Begründung |
|---|---:|---|---|
| Tibetische Silben | ca. 89 % | **hoch** | 97 % im unabhängigen Test, keine falsche Silbe. Rest sind TZ-Feinheiten, die TZ selbst uneinheitlich handhabt. |
| Mantras und Sanskrit | ca. 11 % | **mittel** | Nicht unabhängig getestet. TZ-Mantraschreibungen sind Tradition und lassen sich nur teilweise aus Regeln ableiten. Das Lexikon ist klein. |

Ergebnisse wie „tibetisch *sang*, geschrieben *mam*“ sind nach allen drei Prüfungen sehr
unwahrscheinlich. Offen sind vor allem Konventionsfragen.

---

## 4. Was gebaut ist und was nicht

**Gebaut (reiner Forschungscode, außerhalb von Reader und Workbench, nicht committet):**

- `scripts/phonetics_research/tz_phonetics.py`: der Generator mit beiden Konventionen;
- `evaluate.py`: erzeugt die Umschrift aller 192 Passagen, die Lückenliste und die Mapping-Prüfung;
- `tz_ocr_lines.py` und `crosscheck_observations.py`: Prüfung 2;
- `heldout_eval.py` und `gebetsbuch_heldout.tsv`: Prüfung 3;
- die Ergebnisse in `data/derived/phonetics-research/` (per `.gitignore` von Git ausgeschlossen).

**Nicht gebaut:**

- keine Anbindung an Projektor, Publication Read Model oder Reader;
- keine automatisierten Tests für den Generator;
- kein Neuaufbau des Beobachtungskorpus aus der eigenen Texterkennung;
- keine Wortzusammenschreibung (*dorsche*), keine Lautverschleifungsregeln;
- keine manuelle Korrekturliste (die Datei existiert, ist aber leer);
- kein Konventionsschalter im Reader.

---

## 5. Vorschlag für den Weg in den Reader (noch nicht beschlossen)

### 5.1 Vorab erzeugen, nicht live im Browser

**Empfehlung: Die Umschrift beim Build vorab erzeugen.** Der Reader wird schon heute beim Build aus
Python-Daten erzeugt: Das Skript `convert_sample.py` schreibt `publication.json`. Der Generator
würde dort eingehängt und schreibt die Umschrift pro Passage in die Daten. Der Reader zeigt sie nur
an.

- **Gründe dafür:**
  - Der tibetische Text ändert sich im Reader nicht; die Workbench bearbeitet nur Übersetzungen.
    Eine Berechnung im Browser brächte also nichts.
  - Die Logik bleibt an einer Stelle, in Python. Eine zweite Kopie in TypeScript würde
    auseinanderlaufen.
  - Die Ausgabe ist fest und prüfbar. Jede Änderung am Generator zeigt sich als Unterschied in den
    Daten und lässt sich gegenlesen.
  - Korrekturen kommen über die Korrekturliste hinein, nicht über Code.
- **Nachteil:** Eine Regeländerung wird erst nach einem neuen Build sichtbar. Beim statischen
  Netlify-Build ist das ohnehin der Fall.
- **Live im Browser lohnt sich erst**, wenn Nutzer tibetischen Text selbst eingeben oder ändern.
  Das ist derzeit nicht geplant.

### 5.2 Umschaltung

- **Einfachste gute Variante:** Beide Konventionen werden beim Build erzeugt und zu jeder Passage
  gespeichert. Das kostet wenig Platz. Im Reader gibt es neben „Aussprache“ eine kleine Auswahl
  (etwa „TZ aktuell“ / „TZ Gebetsbuch“). Sie wird wie die anderen Anzeige-Einstellungen im Browser
  gemerkt.
- **Alternative:** Du legst eine Konvention fest, und es gibt keinen Schalter. Das ist schlanker.
  Mehr als eine Konvention lässt sich später jederzeit nachrüsten.

### 5.3 Was sich am Datenformat ändern müsste

- Der Status wechselt von `unreviewed-example` (von Hand) zu etwa `generated-draft` (automatisch,
  ungeprüft). Dazu kommen Generator-Version und Konvention.
- Die heutige Regel bleibt erhalten: Die Aussprachezeilen gehören zu tibetischen Abschnitten, die
  zusammen exakt den Quelltext ergeben.
- Die Herkunft pro Silbe (*confirmed*, *rule_tibetan* …) bleibt in einer Prüfdatei. Sie wandert
  nicht in den Reader.
- Die sechs handgeschriebenen Beispiele würden durch die generierte Fassung ersetzt.

### 5.4 Offene Entscheidungen (Stil- und Produktfragen, ohne Tibetischkenntnisse beantwortbar)

1. Eine Konvention fest oder beide mit Schalter? Welche ist Standard?
2. Mantras silbenweise (*SA MA YA*) oder zusammengeschrieben (*SAMAYA*)?
3. Welcher Hinweis steht im Reader, etwa „automatisch erzeugt, ungeprüft“?
4. Sollen unsichere Silben, vor allem Mantras, sichtbar markiert werden? Oder nur in der Workbench?

### 5.5 Sinnvolle nächste Schritte vor einer Integration

1. Automatisierte Tests für den Generator, mit den Gebetsbuch-Zeilen als Testfälle.
2. Das Mantra-Lexikon anhand der Mantras aus den TZ-Heften erweitern. Das ist die größte
   verbleibende Unsicherheit.
3. Konventionsschalter für die Feinheiten, die das Gebetsbuch zeigt (Genitiv nach u/o, ཅི).
4. Danach die Integration als eigene, freigegebene Aufgabe.
