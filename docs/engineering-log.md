# Engineering-Log

Ausführliches Arbeitsprotokoll. Neueste Einträge unten. Pro Eintrag: Ziel, Vorgehen, Befunde,
Probleme/Sackgassen, Ergebnis, nächster Schritt.

---

## 2026-10-06 — Sitzung 1: Aufräumen, Referenzpaket, Planung (M0)

**Ziel:** Repo aufräumen, Transferpaket einsortieren, Initial-Prompt (01_01) in eigene Spec,
Roadmap und Ausführungsprompt überführen, Arbeitsregeln festlegen. Danach Halt zur Freigabe.

**Ausgangslage:** frisches `uv init`-Projekt (Hello-World in `src/learn_tibetan/__init__.py`),
noch kein Commit, Initial-Prompt und das 48-MB-Zip `references/transliteration/…mit-quelltexten.zip`.

**Vorgehen und Befunde:**

1. `README_UMSCHRIFT.md` im Zip gelesen. Inhalt: Produktionskerne `tz.py` (TZ-Aussprache,
   stdlib-only, Version 1.0.0) und `wylie.py` (EWTS, nutzt Parser aus `tz.py`), 62 fokussierte
   Tests, Forschung/Evidenz, Reader-Integrationsbeispiel, TZ-Scans (47 MB), DILA-Index (7 MB).
   Lizenz: Ursprung proprietär, interne Nutzung.
2. Zip in den Scratchpad entpackt und einsortiert (Tabelle in
   `references/transliteration/README.md`). Engine + Tests in die Projektstruktur, Importpfad
   angepasst (D-002). Große Dateien gitignored (D-003). Original-Zip bleibt lokal liegen.
3. `pytest` per `uv add --dev pytest`: Online-Installation scheiterte (DNS-Timeouts für pypi/npm in
   WSL, auch ohne Sandbox; `curl` lieferte einmal 200, danach nur noch Resolve-Timeouts). Lösung:
   `uv add --dev pytest --offline` aus dem uv-Cache. **62 passed in 1 s** (inkl. DILA-Vergleich,
   da Index lokal vorhanden).
4. Commit `f642cbe` (Scaffold + Referenzen + Initial-Prompt); Working Tree sauber.
5. Engine-Probe für den Lernstoff:
   - Alle 30 Buchstaben: Wylie korrekt (`ka … a`, འ → `'a`, ཨ → `a`).
   - TZ (tz-aktuell) kollidiert bei ཅ/ཆ → *tscha*, ཞ/ཤ → *scha*, ཟ/ས → *sa*, འ/ཨ → *a*.
     Gebetsbuch-Variante kollabiert zusätzlich die Behauchung (ཁ → *ka*). → Mehrdeutigkeitsregel D-005.
   - Vokalformen: ཀི `ki`/`ki`, ཅི `ci`/`tschi`, ཤུ `shu`/`schu`. Zusammensetzung Buchstabe +
     Vokalzeichen funktioniert direkt mit `wylie.syllable`/`tz.render`.
   - `tz.analyse("བསྒྲུབས")` liefert alle Positionen → Grundlage für Kapitel 6 (`analysis`-Feld).
6. Kein UI-Referenzbild unter `references/ui/` vorhanden.
7. Planung geschrieben: `AGENTS.md` (+ `CLAUDE.md` importiert sie), Spec 01_02, Roadmap 01_03,
   Ausführungsprompt 01_04, `CHANGELOG.md`, `docs/decisions.md` (D-001…D-006).

**Interpretation des Auftrags:** „Nur bis Schritt 5“ = Curriculum-Kapitel 1–5. Kapitel 6/7 nur im
Datenmodell vorbereitet (im Plan als Annahme 1 markiert, Owner bestätigt bei Freigabe).

**Probleme:** DNS/Netz in WSL instabil. Für M2 (npm install) wird funktionierendes Netz gebraucht.

**Nächster Schritt:** Freigabe durch den Owner, dann M1 (Content-Pipeline).
