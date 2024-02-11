# Semesterprojekt Chatbot

## Aktuelles

### Hinweis

- Die JS-only Demo im Verzeichnis <i>/demo-js-only</i> kann über lokalen <a href="https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer">Live Server</a> oder <a href="https://emsehub.github.io/semesterprojekt-chatbot/demo-js-only/">hier</a> getestet werden, läuft bis auf Weiteres jedoch nur unter Chrome (<i>import assertions</i> werden aus Sicherheitsgründen nicht von allen Browsern unterstützt, siehe <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#browser_compatibility">hier</a>)


## Anforderungen

Zusammenfassung der Aufgabenstellung zum Semesterprojekt 'Chatbot'

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

- Identifikation des Studenten per Matrikelnummer bei jeder Anfrage
- menschliche, natürlichsprachliche Kommunikation erzeugen und 
- Umgangssprache verstehen
- Aktionen sollen tatsächliche Änderungen in der (simulierten) Datenbank bewirken
- Fehlerbehandlung von Falscheingaben & Edge Cases
  - falsche Matrikelnummer
  - Anmeldung, wenn Prüfung bereits bestanden
  - Notenabfrage, wenn Prüfung noch nicht bestanden
- Chatbot erkennt Absichten (Intents) des Studenten und führt entsprechende Aufgaben aus
- Chatbot erfragt alle für die Erledigung einer Aufgabe benötigten Informationen

### Beispieldialoge

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

## Projekt-Setup 

- Zur Verwaltung von Packages und Virtual Environment das Package "pipenv" installieren, d. h. CMD öffnen und je nach Präferenz einen der folgenden Befehle ausführen:
   ```
   pip install pipenv
   pip install --user pipenv
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
 - Es muss der Interpreter der Virtual Environment verwendet werden:<br>**STRG + Shift + P -> "Python: Select Interpreter" -> "semesterprojekt-chatbot-..." wählen**<br>(auf das Refresh-Icon oben in der Leiste klicken, falls die VE noch nicht aufgeführt ist)

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