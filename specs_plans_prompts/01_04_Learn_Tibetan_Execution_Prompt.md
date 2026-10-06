# 01_04 — Learn Tibetan: Ausführungsprompt (M1–M6)

Du setzt die Learn-Tibetan-PWA um. Lies zuerst, in dieser Reihenfolge und nur einmal:

1. `AGENTS.md` (verbindliche Arbeitsregeln: token-bewusst, Prototyp, Doku, Commit pro Schritt)
2. `specs_plans_prompts/01_02_Learn_Tibetan_Spec.md` (was gebaut wird)
3. `specs_plans_prompts/01_03_Learn_Tibetan_Implementation_Plan.md` (Reihenfolge, Abnahmekriterien)
4. `docs/decisions.md` (getroffene Entscheidungen, Sackgassen) und das Ende von
   `docs/engineering-log.md` (wo wir stehen)

Die Produktvision steht in `01_01_Learn_Tibetan_Initial_Prompt.md`. Lies sie nur bei inhaltlichen
Zweifeln nach; 01_02 hat Vorrang, wo es bewusst abweicht.

## Auftrag

Arbeite die Meilensteine **M1 bis M6** aus 01_03 der Reihe nach ab. Umfang: Curriculum-Kapitel 1–5.
Kapitel 6/7 nur so weit, wie das Datenmodell (`analysis`, `kind`) es schon vorsieht.

Das wichtigste Erlebnis, das zuerst richtig gut werden muss:
**Tibetische Glyphe → sofort erkennen → richtige Wylie-Antwort antippen → nächste.**

## Pro Meilenstein

1. Kurz prüfen, ob decisions.md etwas Relevantes sagt.
2. Umsetzen, in kleinen kohärenten Schritten; die App bleibt ab M2 lauffähig.
3. Gezielt testen (nur der betroffene Bereich; Testumfang laut Spec §11).
4. CHANGELOG (`[Unreleased]`, beim Meilenstein ggf. Version), engineering-log (ausführlich:
   Ziel, Vorgehen, Befunde, Probleme, Sackgassen, nächster Schritt), decisions.md bei Entscheidungen.
5. Commit (Conventional Commits, englisch, Co-Author-Zeile laut Harness), `git status` sauber.

## Harte Regeln (Kurzfassung, Details in AGENTS.md)

- Tibetisch, Wylie, TZ und Audio sind getrennte Felder. Wylie/TZ nur generiert über
  `src/learn_tibetan/phonetics/`, nie von Hand.
- Keine Quizfrage mit mehrdeutiger Antwort: allgemeine P/A-Regel aus Spec §6.4.
- Keine Python-Abhängigkeit zur Laufzeit; kein Cloud-TTS zur Laufzeit.
- Fachliche Unsicherheit in `content/`-Daten mit Notiz, nicht in Logik.
- Wenige Abhängigkeiten; kein UI-Framework, kein Router-/State-Paket.
- Große oder rechtlich eingeschränkte Dateien nie committen.
- Token sparen: keine generierten Dateien komplett lesen, kurze Befehlsausgaben, keine unnötigen
  Regressionstests, keine ungefragten Variantenvergleiche.

## Wann den Owner fragen

Nur bei Entscheidungen, die das Produkt wesentlich ändern (z. B. Audio-Quelle untauglich und keine
gleichwertige Alternative, Lizenzproblem, Abweichung vom Lernpfad). Sonst entscheiden,
dokumentieren und weitermachen.

## Abschluss

Nach M6: README vollständig (Starten, Testen, Content, Transliteration/TZ, Audio ersetzen, PWA
installieren), kurze Retrospektive im engineering-log, offene Punkte für Kapitel 6/7, sauberer Commit.
