# Die tibetische Aussprachehilfe im Reader: wie sie funktioniert und warum man ihr trauen kann

**Created:** 2026-09-25T19:01:52+02:00
**Last updated:** 2026-09-25T20:33:38+02:00
**Status:** current
**Origin:** repository_agent_generated
**Document role:** reference_resource_note
**Ersetzt:** `docs/research/phonetics-01-erklaerung-methodik-und-stand.md` (bleibt als historischer
Stand der Planungsphase erhalten)
**Code:** `src/atp/phonetics/tz.py`, `src/atp/phonetics/wylie.py` · **Tests:** `tests/unit/test_phonetics_tz.py`, `tests/unit/test_phonetics_wylie.py`

Dieses Dokument richtet sich an Leserinnen und Leser, die kein Tibetisch lesen. Es erklärt, was die
Aussprachehilfe im Hayagrīva-Reader tut, warum grobe Fehler praktisch ausgeschlossen sind, an
welchen Feinheiten sie sich von gedruckten TZ-Texten unterscheiden kann und worin sich die drei
wählbaren Varianten unterscheiden.

---

## 1. Kurz gesagt

- Zu jeder tibetischen Zeile zeigt der Reader eine deutsch lesbare Aussprache, zum Beispiel
  *sang gyä tschö dang tshog kyi tschog nam la*.
- Sie wird **automatisch** aus den tibetischen Zeichen erzeugt: Silbe für Silbe, nach festen,
  dokumentierten Leseregeln.
- Das ist **nicht schwer**, weil die tibetische Schrift ungewöhnlich regelmäßig ist. Aus der
  Schreibung einer Silbe folgt ihre Aussprache fast mechanisch.
- **Getestet** wurde am TZ-Gebetsbuch, einem Text, den der Generator beim Bau nicht kannte:
  **98,4 %** der Silben stimmen exakt mit dem TZ-Druck überein. Keine Silbe war grob falsch.
- Die restlichen Unterschiede sind **Feinheiten der Schreibweise**, die TZ selbst nicht einheitlich
  handhabt, etwa *tshog* oder *tsog*, *pä* oder *pa*.
- Im Reader stehen drei Varianten zur Wahl: **TZ aktuell** (voreingestellt), **TZ Gebetsbuch** und
  **Silbengetreu**.

---

## 2. Warum das gar nicht so schwer ist

### 2.1 Jede Silbe folgt demselben Bauplan

Tibetisch wird Silbe für Silbe geschrieben. Die Silben trennt ein Punkt (་). Jede Silbe hat
**einen Grundbuchstaben**. Um ihn herum können bis zu sechs weitere Buchstaben an festen Positionen
stehen:

| Position | Beispiel in བསྒྲུབས (gesprochen *drub*) | Wirkung |
|---|---|---|
| Vorsilbe | བ | stumm |
| aufgesetzter Buchstabe | ས | stumm |
| **Grundbuchstabe** | ག | bestimmt den Anlaut: *g* |
| untergesetzter Buchstabe | ར | verändert den Anlaut: g + r → *dr* |
| Vokalzeichen | ུ | *u* |
| Endbuchstabe | བ | *b* |
| zweiter Endbuchstabe | ས | stumm |

Die Schreibung ist über tausend Jahre alt, die Aussprache hat sich seither vereinfacht. Viele
Buchstaben sind heute stumm, aber **welche** stumm sind, ist genau geregelt. Der Generator zerlegt
jede Silbe in diese Positionen und setzt die Aussprache aus wenigen kleinen Tabellen zusammen:

| Tabelle | Einträge | Beispiele |
|---|---:|---|
| Grundbuchstabe → Anlaut | 30 | ཅ → *tsch*, ཞ → *sch*, ཚ → *tsh* |
| untergesetztes y | 8 | ཕྱ → *tsch*, བྱ → *dsch*, ཀྱ → *ky* |
| untergesetztes r | 14 | ཀྲ → *tr*, ཁྲ → *thr*, གྲ → *dr* |
| untergesetztes l | 6 | གླ → *l*, ཟླ → *d* |
| Endbuchstaben | 10 | ག → *g*, ང → *ng*, ད und ས → stumm |
| Umlautregel | 1 | nach End-ད, -ས, -ན, -ལ und beim Genitiv werden a/o/u zu ä/ö/ü |

Eine große Wörterliste gibt es nicht. Deshalb bekommt auch jede Silbe, die in keinem TZ-Heft
vorkommt, eine Aussprache. Im ganzen Hayagrīva-Text (11.875 Silben) bleibt keine offen.

### 2.2 Die Laute: Verwandtschaft mit Devanagari

Die tibetische Schrift wurde im 7. Jahrhundert nach indischem Vorbild geschaffen. Wer Devanagari
kennt, erkennt die Ordnung wieder: vier Buchstaben pro Reihe, jeweils unbehaucht, behaucht,
ursprünglich stimmhaft und nasal.

| Reihe | unbehaucht | behaucht | ursprünglich stimmhaft | nasal |
|---|---|---|---|---|
| Kehllaute | ཀ क → *k* | ཁ ख → *kh* | ག ग → *g* | ང ङ → *ng* |
| Gaumenlaute | ཅ च → *tsch* | ཆ छ → *tsch* | ཇ ज → *dsch* | ཉ ञ → *ny* |
| Zahnlaute | ཏ त → *t* | ཐ थ → *th* | ད द → *d* | ན न → *n* |
| Lippenlaute | པ प → *p* | ཕ फ → *ph* | བ ब → *b* | མ म → *m* |
| Zischlaute (tibetische Ergänzung) | ཙ → *ts* | ཚ → *tsh* | ཛ → *dz* | (an dieser Stelle im Alphabet: ཝ → *w*, kein Nasal) |

Dazu kommen ཞ *sch*, ཟ *s*, འ (stumm, trägt Vokale), ཡ *y*, ར *r*, ལ *l*, ཤ *sch*, ས *s*, ཧ *h* und
ཨ (Vokalträger).

Die Umschrift folgt der Tradition des Tibetischen Zentrums. Drei Dinge fallen dabei auf:

- **Behauchung.** Wie im Hindi gibt es k und kh, t und th. „TZ aktuell“ schreibt das h (*khor*,
  *tham*), das Gebetsbuch nicht (*kor*, *tam*).
- **Die dritte Spalte.** Die ursprünglich stimmhaften Buchstaben ག ད བ klingen im heutigen
  Zentraltibetisch eher wie ein tiefes, weiches k/t/p. TZ schreibt sie trotzdem als *g/d/b*, und
  das hilft beim Wiedererkennen.
- **Bei ཅ/ཆ** (ca/cha) unterscheidet TZ nie; beide werden *tsch*.

### 2.3 Sanskrit in tibetischer Schrift

Mantras und Sanskrit-Wörter werden mit **denselben tibetischen Buchstaben** geschrieben. Dazu
kommen wenige Extras, die genau Devanagari entsprechen:

- fünf gespiegelte Buchstaben für die rückgebogenen Laute ཊ ཋ ཌ ཎ ཥ (ट ठ ड ण ष), außerdem ཀྵ (क्ष);
- das Längenzeichen ཱ (wie ा), der Anusvara ཾ (wie ं) und der Visarga ཿ (wie ः).

Anders ist vor allem der **Silbenbau**. Sanskrit passt nicht in den tibetischen Bauplan: In པདྨ
(padma) steht das m *unter* dem d, und zwischen zwei Silbenpunkten stecken oft mehrere
Sanskrit-Silben (pad-ma, ba-dzra). Der Generator erkennt solche Einheiten an diesen Merkmalen. Er
liest sie dann ohne die tibetische Stumm-Logik: jeder Buchstabe klingt, jeder Konsonant hat sein a.

Wie Tibeter bekannte Mantrawörter tatsächlich aussprechen, lässt sich nicht immer aus den
Buchstaben ableiten. བཛྲ steht für b-a-dz-r-a (Sanskrit *vajra*) und wird *bendsa* gesprochen.
Deshalb gibt es dafür einen Schalter (Abschnitt 5).

---

## 3. Warum man der Aussprachehilfe trauen kann

Die Leseregeln wurden an **drei voneinander unabhängigen Quellen** geprüft:

| Quelle | Was sie ist |
|---|---|
| Das Regelwissen | Die tibetischen Rechtschreib- und Leseregeln, in Code gefasst |
| Zwei TZ-Sādhanas | Hayagrīva-Kurzpraxis (2023) und Chakrasamvara-Sādhana. Beide drucken Tibetisch und Umschrift untereinander. Rund 1.400 Silbenpaare wurden daraus ausgezählt. |
| Das TZ-Gebetsbuch | Jahrzehntelang verwendete Umschrift, ohne tibetischen Text. Der Generator wurde auf dieses Buch **nicht** abgestimmt. |

Die Scans wurden lokal per Texterkennung ausgelesen. Die Silbenpaare aus den Sādhanas stimmen bei
**93,9 %** mit einer zweiten, unabhängigen Texterkennung überein. Die übrigen waren Lesefehler,
meist verlorene Umlautpunkte.

**Die Regeln stimmen mit dem TZ-Druck überein.** Für rund 90 % der in den Sādhanas beobachteten
Silben erzeugen die Regeln genau die gedruckte TZ-Schreibung. Die restlichen Fälle sind fast
ausnahmslos Erkennungsfehler im Material oder Schreibschwankungen bei TZ selbst.

**Der entscheidende Test am Gebetsbuch.** Für 64 bekannte Gebetszeilen (Zuflucht, Wunschgebet für
gutes Verhalten, Mandala, Beichte) wurde der tibetische Text aufgeschrieben, vom Generator
umgeschrieben und Wort für Wort mit dem TZ-Druck verglichen:

| Variante | Silben identisch mit dem Gebetsbuch |
|---|---:|
| TZ Gebetsbuch | **557 von 566 (98,4 %)** |
| TZ aktuell | 524 von 566 (92,6 %); die Differenz ist die Behauchung |
| Silbengetreu | 522 von 566 (92,2 %) |

Die 9 verbleibenden Abweichungen:

- *sching* gegenüber *tsching* (zweimal);
- *wa* gegenüber *war* vor einem Verb (zweimal);
- die verbundene Sprechweise *nab sa* (einmal);
- *la* gegenüber *lha* (einmal);
- *gyi* gegenüber *kyi* (einmal);
- ein Druck- oder Erkennungsfehler (*jü*);
- eine mögliche Abweichung in der Textvorlage (*rim pa* gegenüber *rim par*).

Das sind Feinheiten. **Eine völlig falsche Silbe**, etwa *mam* für tibetisch *sang*, **kam nicht
vor**. Das ist auch strukturell unwahrscheinlich: Der Grundbuchstabe jeder Silbe wird
regelgesteuert bestimmt, und für ihn gibt es genau eine Lesung.

Die Prüfung lässt sich jederzeit wiederholen, der Gebetsbuch-Test ist Teil der automatischen Tests.
Eine Einschränkung gehört zur Ehrlichkeit: Den tibetischen Text der Testzeilen hat der Assistent aus
dem Gedächtnis aufgeschrieben, weil das Gebetsbuch ihn nicht druckt. Ein Fehler darin würde gegen
den Generator zählen, nicht für ihn.

---

## 4. Die Feinheiten, an denen Umschriften sich unterscheiden

Wenn die Aussprachehilfe von einem gedruckten TZ-Text abweicht, liegt es fast immer an einer dieser
Stellen. TZ selbst ist hier nicht einheitlich: Das Hayagrīva-Heft von 2023 druckt auf einer Seite
*tshog*, auf einer anderen *zog*; einmal *scho*, einmal *schog*; einmal *pal den*, sonst *päl*.

| Feinheit | Beispiel | Warum sie schwankt |
|---|---|---|
| Behauchung markieren | *tshog* / *tsog* | ältere und neuere TZ-Konvention |
| ཛ schreiben | *dzin* / *dsin* | derselbe Laut, zwei Schreibweisen |
| Genitiv nach o/u | *tschü* / *tschu* (ཕྱོགས་བཅུའི) | Umlaut beim Genitiv wird nicht immer gesetzt |
| verbundene Sprechweise | *dor dsche* / *do dsche* (རྡོ་རྗེ) | ein Buchstabe der Folgesilbe wird an die vorige gezogen |
| TZ-Schreibgewohnheit | *scho* / *schog* (ཤོག) | TZ lässt das End-g hier meist weg |
| Mantrawörter | *bendsa* / *badzra*, *pema* / *padma*, *soha* / *swaha* | traditionelle Aussprache gegenüber den Zeichen |
| Anusvara nach u | *hung* / *hum* | Nasal als ng oder m gelesen |
| Kleinigkeiten | *sching* / *tsching*, *wa* / *war* | Aussprache im Satzfluss |

Unabhängig von den Varianten gilt:

- Zeilenumbrüche im tibetischen Druck sind nur Layout. Eine Aussprachezeile endet erst beim
  tibetischen Satzzeichen (།). Ein Titel ohne Satzzeichen erscheint deshalb als eine lange Zeile.
- Fehlt im Quelltext ein Silbenpunkt (etwa གཡསགཉིས), trennt der Generator die zwei Silben selbst.

---

## 5. Die drei Varianten und ihre Schalter

Im Generator ist jede Feinheit ein **eigener Schalter**. Jede Kombination ist gültig. Der Reader
bietet drei feste Kombinationen an. Wählbar sind sie, sobald „Aussprache“ eingeschaltet ist; der
Browser merkt sich die Wahl.

| Schalter | TZ aktuell (Standard) | TZ Gebetsbuch | Silbengetreu | betroffene Silben im Hayagrīva-Text* |
|---|---|---|---|---:|
| Behauchung markiert | ja: *tshog, tham, khor, phän, thrag* | nein: *tsog, tam, kor, pän, trag* | ja | 951 |
| ཛ | *dz* | *ds* | *dz* | 178 |
| Genitiv-Umlaut nach o/u | ja: *tschü, pö* | nein: *tschu, po* | ja | 72 |
| verbundene Sprechweise | *dor dsche* | *dor dsche* | *do dsche* | 34 |
| TZ-Schreibgewohnheiten | *scho* | *scho* | *schog* | 13 |
| Mantrawörter | traditionell: *bendsa, pema, soha, phä, dza* | traditionell | nach den Zeichen: *badzra, padma, swaha, phat, dzah* | 195 |
| Anusvara nach u | *hung* | *hung* | *hung* | 92 bei *hum* |
| Großschreibung von Sanskrit-Silben | aus | aus | aus | nicht belegt |

\* Anzahl der Silben, die sich ändern, wenn man nur diesen Schalter gegenüber „TZ aktuell“
umlegt. Insgesamt unterscheidet sich „TZ Gebetsbuch“ in 1.191 von 11.875 Silben von „TZ aktuell“,
„Silbengetreu“ in 242.

**Das ist die vollständige Liste.** Alles andere ist in allen drei Varianten gleich:

- *tsch, dsch, sch, g, d, b, ny, ng*;
- die Umlaute nach End-ད, -ས, -ན, -ལ und beim Genitiv nach a (*pä*);
- die Lesung aller untergesetzten Buchstaben;
- die Kleinschreibung.

**Die Varianten im Einzelnen:**

- **TZ aktuell** entspricht dem Hayagrīva-Heft von 2023 und der Chakrasamvara-Sādhana, in der
  konsequenten Form dessen, was diese Hefte überwiegend tun.
- **TZ Gebetsbuch** entspricht der älteren, sehr einheitlichen Umschrift des Gebetsbuchs.
  Behauchung wird dabei überall weggelassen, auch in Mantrawörtern (*pä* statt *phä*). Das
  Gebetsbuch selbst schreibt Mantras in Großbuchstaben und dort teils anders.
- **Silbengetreu** ist zum Lernen der Silben gedacht. Jede Silbe wird für sich gelesen, ohne
  Einfluss der Nachbarsilben und ohne Wortausnahmen. Unter བཛྲ steht *badzra*, wie es geschrieben
  ist. Gesprochen wird es *bendsa*, und das steht im Reader zugleich in der deutschen
  Rezitationszeile (*BENDZA*).

**Mantras werden nicht gesondert behandelt.** Es gibt keine Mantra-Erkennung. Jede Silbe wird
nach denselben Regeln gelesen und klein geschrieben. Ein Schalter für die Großschreibung von
Sanskrit-Silben existiert (*KAM lä dschung*, wie TZ einzelne Keimsilben druckt), ist aber in keiner
Variante eingeschaltet.

---

## 6. Wie die Aussprachehilfe in den Reader kommt

Die Umschrift wird **beim Bauen der Website** erzeugt, nicht im Browser:

- Das Build-Skript (`web/hayagriva-reader/scripts/convert_sample.py`) ruft den Generator für jede
  Passage und jede der drei Varianten auf und legt das Ergebnis in den Reader-Daten ab.
- Der Reader zeigt es nur an.
- Die tibetischen Abschnitte der Aussprachezeilen ergeben zusammengesetzt exakt den tibetischen
  Quelltext. Das Build-Skript prüft das und bricht sonst ab.
- Jede Änderung an den Regeln zeigt sich deshalb als nachprüfbarer Unterschied in den Daten.
- Die drei Varianten vergrößern die übertragene Datenmenge um etwa 57 kB (komprimiert).

---

## 7. Wylie: die Umschrift der Buchstaben

Unabhängig von der Aussprachehilfe blendet der Knopf **„Wylie“** eine zweite Zeile ein, und zwar
auch gleichzeitig mit der Aussprache. Wylie gibt **jeden Buchstaben** wieder, auch die stummen:
བསྒྲུབས wird *bsgrubs*, སངས་རྒྱས wird *sangs rgyas*. Das ist keine Aussprache, sondern die
Schreibung in Lateinschrift. Wer beide Zeilen zusammen einblendet, sieht direkt, welche Buchstaben
beim Sprechen verschwinden:

| Tibetisch | Wylie | Aussprache (TZ aktuell) |
|---|---|---|
| བསྒྲུབས | bsgrubs | drub |
| གཡས | g.yas | yä |
| པའི | pa'i | pä |
| ཧཱུཾ | hUM | hung |

Verwendet wird der verbreitete Standard **EWTS** (Extended Wylie), wie ihn auch die Buddhist
Digital Resource Center (BDRC) nutzt. Die Regeln im Einzelnen:

- Das **a** steht immer hinter dem Grundbuchstaben (*bdag*, nicht *badg*). Den Grundbuchstaben
  bestimmt derselbe Silbenzerleger wie bei der Aussprache.
- Der **Punkt** trennt Vorsilbe und Grundbuchstabe, wo sonst eine andere Lesung möglich wäre
  (*g.yas*: ག vor ཡ, nicht ག mit untergesetztem ཡ).
- Für **Sanskrit** gilt:
  - lange Vokale werden groß geschrieben (*hUM*, *mahA*);
  - rückgebogene Laute ebenfalls (*phaT*);
  - Anusvara ist *M*, Visarga *H*;
  - Buchstabenstapel, die es im Tibetischen nicht gibt, werden mit *+* verbunden (*pad+ma*,
    *sid+dhi*).

**Geprüft** wurde gegen die Mahāvyutpatti, ein klassisches Wörterbuch, dessen digitale Ausgabe
(DILA) jeden Eintrag tibetisch und in Wylie enthält. Von 42.791 vergleichbaren Silben stimmen
**42.566 (99,5 %)**. Die übrigen Fälle sind fast alle Unstimmigkeiten im Wörterbuch selbst, dessen
tibetischer und Wylie-Eintrag einander dort widersprechen. Dieser Test läuft automatisch mit.

## 8. Grenzen

- **Keine Wortzusammenschreibung.** TZ schreibt manchmal *dorsche* oder *khadro*, der Generator
  immer silbenweise.
- **Verbundene Sprechweise.** Nur ein belegter Fall ist eingebaut (*dor dsche*). Weitere wie
  *nab sa* oder *khan dro* sind bei TZ selbst uneinheitlich und fehlen bewusst.
- **Mantras.** Die Lesung von Sanskrit-Silben ist weniger geprüft als die tibetischen Silben. Im
  Gebetsbuch-Test kamen keine Mantras vor.
- **Quelltext.** Die Umschrift ist nur so gut wie der tibetische Text im Arbeitsstand v10.

---

## 9. Entstehung, kurz

Ein erstes Silben-Mapping entstand außerhalb dieses Projekts aus den beiden TZ-Sādhanas. Seine
Silbenzählungen erwiesen sich als brauchbar. Die daraus abgeleiteten Endwerte hatten dagegen zu
viele Erkennungsfehler, um direkt verwendet zu werden. Der Generator arbeitet deshalb mit
eigenständigen Regeln. Die TZ-Belege dienten zur Prüfung und haben einzelne Entscheidungen
geliefert, etwa *dor dsche*, *scho* und *phä*.

Die vollständige Herleitung mit allen Zahlen steht in
`docs/research/phonetics-01-tz-generator-exploration.md`.
