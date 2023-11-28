# Semesterprojekt Chatbot

## Requirements

Zusammenfassung der Aufgabenstellung zum Semesterprojekt 'Chatbot'

### Aktueller Hinweis

- JS-Only-Demo im Verzeichnis <i>/gui</i> kann über lokalen <a href="https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer">Live Server</a> getestet werden, läuft bis auf Weiteres jedoch nur unter Chrome (<i>import assertions</i> werden aus Sicherheitsgründen nicht von allen Browsern unterstützt, siehe <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#browser_compatibility">hier</a>)

### Aufgaben des Chatbots (Features/Tasks)

- Änderung der Adresse nach Umzug
- Änderung des Nachnamens nach Heirat
- Anmeldung zu einer Prüfung
- Abmeldung von einer Prüfung
- Abfrage Status der Prüfungsanmeldung
  - angemeldet | nicht angemeldet | Prüfung bereits abgeschlossen
- Abfrage Note zu bestandener Prüfung
  - Fehler, falls Prüfung noch nicht bestanden wurde

### Environment:

- Identifikation des Studenten per Matrikelnummer bei jeder Anfrage (dient quasi als Passwort/Legitimation)
- Umgangssprache verstehen (ggf. unklare Anfrage)
- menschliche, natürlichsprachliche Kommunikation (freundliche, flüssige Sprachweise)
- Aktionen sollen tatsächliche Änderungen in der Datenbank bewirken
- Fehlerbehandlung von Falscheingaben & EdgeCases
  - falsche Matrikelnummer
  - unerlaubte Anmeldung (Prüfung bereits bestanden) oder Notenabfrage (Prüfung noch nicht bestanden)
- bei unklaren Anfragen: im Zweifel Nachfragen des Chatbots (fehlende Informationen erfragen, Verifizierung des Intents)
  - Achtung: Anfragen zu Prüfungen (An-/Abmeldung etc.) sind recht ähnlich --> Sicherstellen, dass die richtige Aktion durchgeführt wird!
- Kreativität bei der Lösung, hinreichende Komplexität durch NLP

### Benötigte Mock-Daten (Datenbank)

- Studenten (mind. 5) mit...
  - Matrikelnummer,
  - Namen,
  - Adresse
  - Prüfungen
    - angemeldete
    - bestandene/nicht-bestandene
- Lehrveranstaltungen (mind. 5) mit...
  - d

## TODO

- intents.json ergänzen
- restliche nlp schritte durchführen (nlp pipeline)
- wie können die aussagen zu intents gematcht werden?
  - beispiele online recherchieren

## Grober Plan

- Begrüßung des Users
- Chatbot loop, user input einlesen
- Input mit NLP zerlegen
- Satzbestandteile analysieren (NLP Pipeline)
- Intent des Nutzers ermitteln
- mögliche Antwort aus vorgefertigten Texten auswählen
- Aktion durch User bestätigen lassen
- Aktion durchführen & Infos dazu ausgeben
- nach weiterem Anliegen fragen (repeat loop)
- profit
