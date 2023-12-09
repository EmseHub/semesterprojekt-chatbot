# Semesterprojekt Chatbot

## Requirements

Zusammenfassung der Aufgabenstellung zum Semesterprojekt 'Chatbot'

### Aktueller Hinweis

- JS-Only-Demo im Verzeichnis <i>/gui</i> kann über lokalen <a href="https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer">Live Server</a> oder <a href="https://emsehub.github.io/semesterprojekt-chatbot/gui/">hier</a> getestet werden, läuft bis auf Weiteres jedoch nur unter Chrome (<i>import assertions</i> werden aus Sicherheitsgründen nicht von allen Browsern unterstützt, siehe <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#browser_compatibility">hier</a>)

### Aufgaben des Chatbots (Features/Tasks)

- Änderung der Adresse nach Umzug
- Änderung des Nachnamens nach Heirat
- Anmeldung zu einer Prüfung
- Abmeldung von einer Prüfung
- Abfrage Status der Prüfungsanmeldung
  - nicht angemeldet | angemeldet und nicht abgeschlossen | angemeldet und abgeschlossen
- Abfrage Note zu bestandener Prüfung
  - Falls Prüfung nicht bestanden ist, Feedback über Status der Prüfungsanmeldung

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

### Offene Fragen

- Identitätsabfrage je Anliegen oder je Session/Chataufruf?
- NLTK oder spaCy?
- 1 Token == 1 Wort?
- Rechtschreibprüfung/Autokorrektur vorab? Auf Satz- oder Wortebene?
- Stop-Words erst vor Lemmatization/Stemming entfernen, oder direkt zu Beginn?
- Lemmatization UND/ODER Stemming?
- Co-reference resolution weglassen?

### Projekt-Setup 

- Zur Verwaltung von Packages und Virtual Environment das Package "pipenv" installieren, d. h. CMD öffnen und folgenden Befehl eingeben:
   ```
   pip install pipenv
   ```
 - Projektorder in VS Code öffnen, ggf. bisherige Environments (Ordner "env") löschen und im Terminal folgenden Befehl eingeben, um eine neue pipenv-Umgebung einzurichten (ein lokales Verzeichnis außerhalb des Projektordners wird angelegt, s. u.).
   ```
   pipenv install
   ```
 - Derselbe Befehl installiert automatisch alle im Projekt verwendeten Packages, sofern welche vorhanden sind (d. h. sofern Pipfile und Pipeline.lock bestehen, die Informationen über Packages enthalten)

 - pipenv-Umgebung muss aktiviert werden via:
   ```
   pipenv shell
   ```
 - pipenv-Umgebung kann später deaktiviert werden via:
   ```
   exit
   ```
 - **Von nun an sollten Packages *immer* via *pipenv* installiert bzw. deinstalliert werden**:
   ```
   pipenv install beispielpackage
   pipenv uninstall beispielpackage
   ```
 - Es sollte der Interpreter der Virtual Environment verwendet werden:<br>STRG + Shift + P -> "Python: Select Interpreter" -> "semesterprojekt-chatbot-..." wählen

 - Pfad zum Verzeichnis des Virtual Environments ausgeben:
   ```
   pipenv --venv
   ```
- Falls zum Ausführen von Python-Files die Extension *Code Runner* verwendet wird, muss in den lokalen Workspace-Settings (JSON) folgender Eintrag mit dem Pfad zur Virtual Environment ergänzt werden
   ```json
   "code-runner.executorMap": {
     "python": "C:\\Users\\...\\semesterprojekt-chatbot-...\\Scripts\\python -u"
   }
   ```
- Hinweis: NTLK benötigt einige gesonderte Downloads, daher ist vor Verwendung des Chatbots einmalig die Datei *setup.py* auszuführen

## NLP-Pipeline

1. Tokenization (auf Wortebene)
2. Automatische Rechtschreibkorrektur auf Wortebene
3. Stop-Words entfernen
4. Part-of-Speech-Tagging ((PoS-Tagging))
5. Named Entity Recognition (NER)
6. Lemmatization [oder Stemming]
7. [Co-reference resolution]

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

## Beispieldialoge

- Adressänderung A
  - Studierender: Hallo, ich bin letzte Woche umgezogen und wollte meine neue Adresse mitteilen.
  - Chatbot: Sehr gern. Bitte nennen Sie Ihre Matrikelnummer, damit ich Sie im System aufrufen kann.
  - Studierender: Meine Mat.Nr. ist 123456.
  - Chatbot: Vielen Dank, Frau Meier. Bitte nennen Sie mir Ihre neue Adresse.
  - Studierender: Ich wohne jetzt in der Hauptstraße 12 in Dortmund.
  - Chatbot: Vielen Dank. Können Sie mir bitte noch die Postleitzahl der Hauptstraße 12 in Dortmund nennen?
  - Studierender: 44143
  - Chatbot: Vielen Dank. Ich fasse noch einmal zusammen: Sie sind umgezogen und Ihre neue Adresse lautet Hauptstraße 12 in 44143 Dortmund. Ist dies korrekt?
  - Studierender: Ja
  - Chatbot: Vielen Dank, ich habe die Änderung vorgenommen.
- Adressänderung B
  - Studierender: Guten Morgen, mein Name ist Meier (123456) und ich bin umgezogen. Ich wohne jetzt in 44143 Dortmund und zwar in der Hauptstraße 12. Bitte ändern Sie meine Anschrift.
  - Chatbot: Vielen Dank, Frau Meier. Ich fasse noch einmal zusammen: Sie sind umgezogen und Ihre neue Adresse lautet Hauptstraße 12 in 44143 Dortmund. Ist dies korrekt?
  - Studierender: Ja
  - Chatbot: Vielen Dank, ich habe die Änderung vorgenommen.
