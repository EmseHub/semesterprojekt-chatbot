# Semesterprojekt Chatbot

## Aktuelles

### Hinweis

- Eine rudimentäre JS-only Demo im Verzeichnis <i>demo-js-only</i> kann über lokalen <a href="https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer">Live Server</a> oder <a href="https://emsehub.github.io/semesterprojekt-chatbot/demo-js-only/">hier</a> getestet werden, läuft bis auf Weiteres jedoch nur unter Chrome (<i>import assertions</i> werden aus Sicherheitsgründen nicht von allen Browsern unterstützt, siehe <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#browser_compatibility">hier</a>)


## Anforderungen

Das Projekt umfasst einen Chatbot zur automatisierten Verarbeitung von Anfragen von Studierenden an das Prüfungsamt oder Studienbüro einer Hochschule.

### Aufgaben des Chatbots

- Änderung der Adresse nach Umzug
- Änderung des Nachnamens nach Heirat
- Anmeldung zu einer Prüfung
- Abmeldung von einer Prüfung
- Abfrage Status der Prüfungsanmeldung
  - nicht angemeldet | angemeldet und nicht abgeschlossen | angemeldet und abgeschlossen
- Abfrage Note zu bestandener Prüfung
  - Falls Prüfung nicht bestanden ist, Feedback über Status der Prüfungsanmeldung

### Rahmenbedingungen

- Identifikation der Studierenden ist bei jeder Anfrage erforderlich und anhand der Matrikelnummer realisierbar
- menschliche, natürlichsprachliche Kommunikation erzeugen 
- Umgangssprache verstehen
- Aktionen sollen tatsächliche Änderungen in der (simulierten) Datenbank bewirken
- Fehlerbehandlung von Falscheingaben und Edge Cases
  - falsche Matrikelnummer
  - Anmeldung, wenn Prüfung bereits bestanden
  - Notenabfrage, wenn Prüfung noch nicht bestanden
- Chatbot erkennt Absichten (Intents) der Studierenden und führt entsprechende Aufgaben aus
- Chatbot erfragt alle für die Erledigung einer Aufgabe benötigten Informationen

### Beispieldialoge

- Adressänderung A

  - ```Hallo, ich bin letzte Woche umgezogen und wollte meine neue Adresse mitteilen.```
  - >Sehr gern. Bitte nennen Sie Ihre Matrikelnummer, damit ich Sie im System aufrufen kann.
  - ```Meine Mat.Nr. ist 123456.```
  - >Vielen Dank, Frau Meier. Bitte nennen Sie mir Ihre neue Adresse.
  - ```Ich wohne jetzt in der Hauptstraße 12 in Dortmund.```
  - >Vielen Dank. Können Sie mir bitte noch die Postleitzahl der Hauptstraße 12 in Dortmund nennen?
  - ```44143```
  - >Vielen Dank. Ich fasse noch einmal zusammen: Sie sind umgezogen und Ihre neue Adresse lautet Hauptstraße 12 in 44143 Dortmund. Ist dies korrekt?
  - ```Ja```
  - >Vielen Dank, ich habe die Änderung vorgenommen.

- Adressänderung B

  - ```Guten Morgen, mein Name ist Meier (123456) und ich bin umgezogen. Ich wohne jetzt in 44143 Dortmund und zwar in der Hauptstraße 12. Bitte ändern Sie meine Anschrift.```
  - >Vielen Dank, Frau Meier. Ich fasse noch einmal zusammen: Sie sind umgezogen und Ihre neue Adresse lautet Hauptstraße 12 in 44143 Dortmund. Ist dies korrekt?
  - ```Ja```
  - >Vielen Dank, ich habe die Änderung vorgenommen.


## Projekt-Setup 

### 1. Pipenv/Virtual Environment einrichten und verwendete Packages installieren

- Zur Verwaltung von Packages und der Virtual Environment das Package "pipenv" installieren, d. h. CMD öffnen und je nach Präferenz einen der folgenden Befehle ausführen:
   ```
   pip install pipenv
   pip install --user pipenv
   ```
 - Projektorder mit VS Code öffnen, ggf. bisherige Environments (Ordner "env") löschen und im Terminal (STRG + Shift + Ö) unter dem Pfad des Projektorders folgenden Befehl ausführen, um eine neue pipenv-Umgebung einzurichten (ein lokales Verzeichnis außerhalb des Projektordners wird angelegt, s. u.).
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
 - VS Code muss auf den Interpreter der Virtual Environment gesetzt werden:<br>**STRG + Shift + P -> "Python: Select Interpreter" -> "semesterprojekt-chatbot-..." wählen**<br>(auf das Refresh-Icon oben in der Leiste klicken, falls die VE noch nicht aufgeführt ist)

 - Mit folgendem Befehl kann man den Pfad zum Verzeichnis des Virtual Environments ausgeben:
   ```
   pipenv --venv
   ```
- Falls zum Ausführen von Python-Files die Extension *Code Runner* verwendet wird, muss in den lokalen Workspace-Settings (JSON) folgender Eintrag mit dem Pfad zur Virtual Environment ergänzt werden
   ```json
   "code-runner.executorMap": {
     "python": "C:\\Users\\...\\semesterprojekt-chatbot-ANPASSEN\\Scripts\\python -u"
   }
   ```

### 2. Datei *setup.py* ausführen
- NTLK benötigt gesonderte Downloads, daher ist vor Verwendung des Chatbots einmalig die Datei *setup.py* auszuführen

### 3. Eingabe über Web-Frontend oder Terminal starten
- Je nach Präferenz *run_in_webfrontend.py* oder *run_in_terminal.py* ausführen, um die Interaktion zu starten



## Known Issues

### Nachnamen ändern
- Wenn Studierende ihren neuen Nachnamen bereits genannt haben und sich erst in einer späteren Nachricht mit ihrer Matrikelnummer identifizieren, wird der Nachname erneut erfragt. Dieses Problem tritt nicht auf, wenn der neue Nachname und die Matrikelnummer in derselben Nachricht gesendet werden.

  Grund: Das Student-Objekt ist für die Ermittlung des Nachnamens im Text erforderlich. Es könnte sein, dass Studierende ihren vollen Namen angeben. Dem Erkennungsalgorithmus muss bekannt sein, wie der Vorname lautet, damit er gezielt danach suchen kann, ob es im Text einen anderen als den bestehenden Nachnamen hinter dem Vornamen gibt. Zudem muss der Algorithmus den Vornamen vom neuen Nachnamen abtrennen können.


- Nachnamen, die ein oder mehrere Wörter enthalten, die mit einem Kleinbuchstaben beginnen, werden nur dann korrekt erkannt, wenn sie hinter einem Doppelpunkt angegeben werden ("Mein Nachname hat sich geändert in: Freiherr von Mustersee"). 

### Angaben korrigieren 
- Wenn Studierende die finale Rückfrage vor dem Abschließen der Aufgabe nicht bestätigen (oder die Bearbeitung schon vorher unterbrechen), gehen alle der Aufgabe zugeordneten Informationen verloren. Dies gilt auch dann, wenn z. B. bei der Angabe des Straßennamens ein kleiner Tippfehler unterlaufen ist und lediglich diese Information korrigiert werden soll. Für jede Korrektur muss der Task neu begonnen werden.

### Anliegen mitteilen
- Es können nicht mehrere Anliegen bzw. Tasks gleichzeitig erkannt und bearbeitet werden. Solange ein Task offen ist, beziehen sich alle Nachrichten ausschließlich auf ihn.


