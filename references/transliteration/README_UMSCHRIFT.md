# Transferpaket: Tibetische Aussprache- und Wylie-Generatoren

**Created:** 2026-10-06T01:44:58+02:00  
**Last updated:** 2026-10-06T01:49:03+02:00  
**Status:** current  
**Origin:** repository_agent_generated  
**Document role:** historical_methodology_handoff

Dieses Paket ist ein absichtlich breiter **Codesteinbruch** aus dem Tāranātha ATP Workbench.
Es soll einem anderen Agenten erlauben, die beiden Generatoren zu verstehen, zu testen, zu
extrahieren und in einem anderen Projekt neu einzubinden. Es ist kein eigenständig
veröffentlichtes Python-Paket und enthält keinen neu geschriebenen Generatorcode.

## Schnellster Einstieg

Die produktiven Kerne sind:

- `src/atp/phonetics/tz.py`: Tibetisch → deutsch lesbare Aussprachehilfe im Stil des
  Tibetischen Zentrums. Standardbibliothek-only, deterministisch, Version `1.0.0`.
- `src/atp/phonetics/wylie.py`: Tibetisch → Wylie/EWTS. Nutzt Parser und Segmentierung aus
  `tz.py`; daher beide Dateien zusammen übernehmen.

Minimaler Aufruf aus dem Wurzelverzeichnis dieses Pakets:

```python
from atp.phonetics import tz, wylie

text = "སངས་རྒྱས་ཆོས།"

print(tz.render(text))                    # sang gyä tschö
print(tz.render(text, "tz-gebetsbuch"))
print(wylie.render(text))                 # sangs rgyas chos
```

Zum Import entweder `src/` auf `PYTHONPATH` setzen oder nur `src/atp/phonetics/` in ein eigenes
Package kopieren und den Import in `wylie.py` anpassen. Die Produktionsmodule selbst benötigen
keine Drittanbieterbibliothek. Python 3.11 oder neuer entspricht dem Ursprungsprojekt.

## Öffentliche Schnittstellen

### Aussprache (`tz.py`)

- `render(text, variant_or_options="tz-aktuell") -> str`: kompakte Ausgabe; Phrasen werden mit
  ` / ` verbunden.
- `generate(text, variant_or_options="tz-aktuell") -> list[Line]`: strukturierte Zeilen mit dem
  exakten tibetischen Quellslice, der Aussprache und den analysierten Silben.
- `VARIANTS`: drei Presets `tz-aktuell`, `tz-gebetsbuch`, `silbengetreu`.
- `Options`: unabhängige Schalter für Behauchung, `dz`/`ds`, Genitiv-Umlaut, verbundene
  Sprechweise, TZ-Sonderformen, Sanskrit-Lesung, Anusvara und Großschreibung.
- `analyse`, `segment`, `split_syllables`, `is_sanskrit`: wiederverwendbare Parserbausteine.

### Wylie (`wylie.py`)

- `render(text) -> str`: kompakte EWTS-Ausgabe.
- `generate(text) -> list[Line]`: dieselben exakten Quellslices wie `tz.generate`; dadurch lassen
  sich Original, Aussprache und Wylie zeilenweise parallel anzeigen.
- `syllable(text) -> str`: einzelne tibetische oder Sanskrit-Silbe nach EWTS.

Beide `generate`-Funktionen erhalten die Quelle als byte-exakt zusammensetzbare Slices:
`"".join(line.tibetan for line in generate(text)) == text`. Diese Invariante ist für UI- und
Provenienz-Anbindungen wichtiger als die bequeme `render`-Ausgabe.

## Testen

Mit installiertem `pytest`:

```bash
PYTHONPATH=src pytest -q tests/unit/test_phonetics_tz.py tests/unit/test_phonetics_wylie.py
```

Beim Erstellen dieses Pakets liefen die fokussierten Tests mit **62 passed**. Der
Gebetsbuch-Held-out-Test verlangt mindestens 97 % exakte Token-Übereinstimmung und erreicht im
dokumentierten Stand 98,4 %. Der mitgelieferte lokale DILA-Mahāvyutpatti-Index macht auch den
großen Wylie-Vergleich reproduzierbar: 42.566 von 42.791 Silben (99,47 %) stimmen überein.

Der „große lokale DILA-Index“ ist kein Modell und keine Generatorabhängigkeit. Es ist eine lokal
aus dem DILA-TEI-Export erzeugte JSON-Datei mit 9.379 Wörterbucheinträgen und parallelen
tibetischen/Wylie-Formen. Der Test rendert die tibetische Form selbst und vergleicht sie mit der
von DILA angegebenen Wylie-Form. Im Paket liegt nur der dafür benötigte 7,3-MB-Index, nicht der
gesamte 177-MB-Indexbestand des Ursprungsprojekts.

Wichtige Einschränkung: Die tibetische Seite des Gebetsbuch-Fixtures wurde mangels tibetischem
Drucktext durch den damaligen Agenten aus dem Gedächtnis rekonstruiert. Sanskrit-/Mantra-Lesungen
sind nicht durch einen unabhängigen Held-out-Test abgesichert.

## Inhalt und wofür er gedacht ist

- `src/`: produktiver, wiederverwendbarer Code.
- `tests/`: kompakte Verhaltensspezifikation und Held-out-Fixture.
- `docs/tz-umschrift.md`: aktuelles deutschsprachiges Funktions- und Vertrauensdokument.
- `docs/research/phonetics-01-tz-generator-exploration.md`: Entstehung, Messungen, Fehlversuche
  und verbleibende Unsicherheit.
- `research/`: explorative Vorgängerskripte. Sie sind nicht der Produktionsgenerator und haben
  teils Ursprungsrepo-spezifische Pfade; nützlich zum Reverse Engineering der Entscheidungen.
- `reference_phonetics/`: abgeleitete Mappings, Beobachtungskorpus und Provenienzdokument. Der
  Produktionsgenerator hat darauf **keine Laufzeit- oder Build-Abhängigkeit**.
- `evidence_outputs/`: ausgewählte erzeugte Audit-, Gap- und Vergleichsresultate aus dem
  Forschungsstand sowie die 105 bereits erzeugten OCR-Seitentexte; Belege und Diagnosematerial,
  keine Laufzeitdaten.
- `data/reference_resources/`: DILA-Mahāvyutpatti-Prüfindex am vom Test erwarteten Pfad und das
  zugehörige Ressourcenmanifest. Nur für Evaluation, nicht für die Generatorlaufzeit.
- `primary_sources/tz_scans/`: drei owner-supplied TZ-PDF-Scans als interne Primärevidenz. Die
  beiden Sādhanas zeigen Tibetisch und TZ-Umschrift parallel; das Gebetsbuch liefert die
  unabhängige Vergleichskonvention ohne tibetischen Drucktext.
- `integration_example/`: reale Reader-Projektion, Tests und TypeScript-Read-Model als Beispiel
  für Einbettung und Datenvertrag. Diese Dateien sind nicht standalone.
- `design/`: der ausgeführte Integrationsprompt als historische Designspur.
- `project_metadata/pyproject.toml`: Umgebung und Ursprungsprojekt-Metadaten; nicht als schlanke
  Paketdefinition missverstehen.

## Was bewusst fehlt

Es fehlen weiterhin das allgemeine OCR-System, der vollständige Reader, die zwei anderen großen
lokalen Wörterbuch-Indizes und der vollständige Hayagrīva-Korpus, weil sie für Generator,
Reverse Engineering und fokussierte Evaluation nicht erforderlich sind.

## Lizenz- und Vertrauenshinweis

Das Ursprungsprojekt deklariert in `pyproject.toml` `Proprietary`. Dieses Transferpaket erteilt
keine zusätzliche Lizenz und keine Erlaubnis zur Veröffentlichung. Der Owner hat die Verwendung der
drei TZ-Scans im anderen eigenen Projekt ausdrücklich freigegeben; das ist als interne
Projektfreigabe zu verstehen, nicht als Aussage über allgemeine Publikations- oder
Weiterverteilungsrechte. Beim DILA-Datensatz lautet der dokumentierte Status
`redistribution_not_assessed`; auch er ist hier für den internen Transfer enthalten. Vor einer
Veröffentlichung oder Weitergabe außerhalb dieses Projektkontexts müssen Code- und Datenrechte
geklärt werden. Die Aussprache ist eine praktische TZ-artige Lesehilfe, keine phonetisch oder
dialektologisch normative Transkription.

## Empfohlene Extraktionsreihenfolge für einen anderen Agenten

1. `tz.py`, `wylie.py` und die beiden Unit-Tests lesen.
2. Die beiden Produktionsdateien gemeinsam in das Zielprojekt kopieren oder den Parser als
   gemeinsames internes Modul herauslösen.
3. Zuerst die vorhandenen 62 fokussierten Tests unverändert zum Laufen bringen.
4. Die `generate`-Slice-Invariante und Generator-Version im Zieldatenmodell erhalten.
5. Eigene Korpusbeispiele und fachlich geprüfte Goldzeilen als zusätzliche Tests ergänzen.
6. Erst danach Regeln, Varianten oder Mantra-Ausnahmen verändern; jede Abweichung vom TZ-Profil
   als eigenes Preset oder explizite Option dokumentieren.
