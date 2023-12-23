<!-- SYNTAX -->
<!-- https://docs.github.com/de/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax -->

# Semesterprojekt Chatbot

- Die JS-only Demo im Verzeichnis <i>/demo-js-only</i> kann über lokalen <a href="https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer">Live Server</a> oder <a href="https://emsehub.github.io/semesterprojekt-chatbot/demo-js-only/">hier</a> getestet werden, läuft bis auf Weiteres jedoch nur unter Chrome (<i>import assertions</i> werden aus Sicherheitsgründen nicht von allen Browsern unterstützt, siehe <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#browser_compatibility">hier</a>)

## Aufgabe

In diesem Semesterprojekt soll auf Basis schon existierender Bibliotheken ein Chatbot entwickelt werden, der ein Studienbüro unterstützt. Der Chatbot soll dabei Fragen von Studierenden beantworten und Änderungen im Prüfungssystem vornehmen können.

### Requirements

Der Chatbot soll aus den Anfragen der Studierenden deren Intention erkennen und passend antworten bzw. handeln. Dabei werden die Studierenden anhand ihrer Matrikelnummer identifiziert. Wenn der Chatbot eine Anfrage nicht bearbeiten kann, soll er eine entspechende Fehlermeldung ausgeben. Bei unklaren Dialogen sollte der Chatbot nachfragen, ob er das Richtige verstanden hat, um nicht versehentlich falsch zu handeln. Folgenden Anforderungen sollte der Chatbot entsprechen:

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

### Aufgaben des Chatbots (Features/Tasks)

- Änderung der Adresse nach Umzug
- Änderung des Nachnamens nach Heirat
- Anmeldung zu einer Prüfung
- Abmeldung von einer Prüfung
- Abfrage Status der Prüfungsanmeldung
  - nicht angemeldet | angemeldet und nicht abgeschlossen | angemeldet und abgeschlossen
- Abfrage Note zu bestandener Prüfung
  - Falls Prüfung nicht bestanden ist, Feedback über Status der Prüfungsanmeldung

### Beispieldialoge

Im Folgenden sind die beiden Beispieldialoge aus der Aufgabenstellung aufgelistet. Natürlich kann der Chatbot aber auch andere Anfragen bearbeiten.

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

## Implementierung / Grundlegender Aufbau

In den folgenden Abschnitten ist die Implementierung des Chatbots zu finden.

### Datenquellen

Zur Simulation der Datenbank der Hochschule haben wir JSON-Dateien verwendet. In diesen Dateien werden Informationen gespeichert und je nach Anfrage vom Chatbot geändert.
- In der Datei "data-courses.json" befinden sich alle Kurse der Hochschule. Die Kurse besitzen jeweils eine ID, einen Namen und die Lehrperson, die diesen Kurs ausführt. 
- Die Datei "data-students.json" enthält alle Studierenden der Hochschule. Für jeden Studierenden wird eine Matrikelnummer, ein Vor- und Nachname, die Adresse, ein Profilbild sowie das Datum, an der die Daten des Students zuletzt geändert wurden, gespeichert. Außerdem werden pro Student die Prüfungen gespeichert, die angemeldet oder schon geschrieben sind.

    ```json
    Code data-courses
    ```

    ```json
    Code data-students
    ```

### Intents

Damit der Chatbot die Intention aus den Anfragen der Studierenden erkennen kann, müssen Intents definiert werden. Intents beschreiben die Absicht oder das Ziel des Nutzers, wie beispielsweise die Absicht, seine Adresse zu ändern. Der Chatbot überprüft bei einer Anfrage, ob ein Thema angesprochen wurde, das er kennt. Er überprüft also, ob er einen Intent erkennt. 
Unsere Intents haben wir in der JSON-Datei "intents.json" definiert.
Jeder Intent besitzt einen "tag", "patterns", "responses", einen "context" und einen "type".
- "tag": der Name des Intents; hiermit wird der Intent identifiziert
- "patterns": enthält Wörter, die in den Anfragen enthalten sind, wenn es sich um den jeweiligen Intent handelt; daran erkennt der Chatbot, um welches Thema es sich handelt
- "responses": enthält Antwortmöglichkeiten für den Chatbot, die zum Intent passen. Diese werden zufällig ausgewählt.
- "context": ??
- "type": beschreibt die Art des Intents, also ob es sich um eine Aufgabe oder nur ein Gespräch handelt; bei "task" muss der Chatbot etwas im System anpassen, bei "chat" muss der CHatbot nur antworten

Folgende Intent-Möglichkeiten existieren bei unserer Aufgabenstellung:
- "hilfe": Der Studierende fragt nach Hilfe
- "danke": Der Studierende bedankt sich
- "begrüßung": Der Studierende begrüßt den Chatbot
- "verabschiedung": Der Studierende verabschiedet sich vom Chatbot
- "bestätigung": Der Studierende bestätigt die Aussage vom Chatbot
- "verneinung": Der Studierende verneint die Aussage vom Chatbot
- "adressänderung": Der Studierende möchte seine Adresse ändern
- "namensänderung": Der Studierende möchte seinen Nachnamen ändern
- "prüfungsanmeldung": Der Studierende möchte sich zu einer Prüfung anmelden
- "prüfungsabmeldung": Der Studierende möchte sich von einer Prüfung abmelden
- "statusabfrage": Der Studierende möchte den aktuellen Status einer Prüfung wissen
- "notenabfrage": Der Studierende möchte die Note einer Prüfung wissen

    ```json
    Code intents
    ```

### Schritte des Chatbots

**Preprocessing mit NLP-Pipeline:**

Im ersten Schritt zerlegt der Chatbot die Anfrage des Studierenden mit Hilfe von Natural Language Processing (NLP). Dabei folgt der Chatbot der NLP-Pipeline, welche eine festgelegte Abfolge von aufeinander aufbauenden Verarbeitungsschritten bezeichnet.

Zuerst noch Normalization? -> Text in Kleinbuchstaben konvertieren & Satzzeichen entfernen

1. Tokenization: Bei der Tokenization wird der Text in einzelne Bestandteile (Tokens) zerlegt. Der Text wird dabei zum Beispiel in seine einzelnen Wörter zerlegt.
2. Stop-Word-Removal: Stoppwörter, also Wörter, die dem Verständnis des Textes nicht weiterhelfen, werden entfernt.
3. Part-of-Speech-Tagging (PoS-Tagging): Die einzelnen Wörter werden ihren Wortarten zugeordnet. Das Word "laufen" ist beispielsweise ein Verb, während das Wort "schnell" ein Adjektiv ist.
4. Named Entity Recognition (NER): NER versucht, Eigennamen erkennen. Diese sogenannten "Named Entities" sind zum Beispiel Namen von Personen, Orten oder Firmen. NER-Methoden nutzen dazu bestehende Wörterbücher, welche eine Liste bereits bekannter Entitäten enthalten.
5. Stemming & Lemmatization: Hierbei werden die Wörter auf ihren Wortstamm zurückgeführt. Das Wort "ging" wird somit beispielsweise zum Wortstamm "gehen".

Danach noch Co-reference resolution? -> herausfinden, ob sich zwei Wörter eines Textes auf dieselbe Entität beziehen

    ```
    Code preprocessing
    ```

**Intent Matching:**

noch erweitern

- Intent des Nutzers ermitteln

    ```
    Code intent matching
    ```

**Regelwerk**

noch erweitern 

- mögliche Antwort aus vorgefertigten Texten auswählen
- Aktion durch User bestätigen lassen
- Aktion durchführen & Infos dazu ausgeben
- nach weiterem Anliegen fragen (repeat loop)

    ```
    Code Regelwerk
    ```

## DER EINZIG WICHTIGE ABSCHNITT [In Jupyter-Notebook mit Beispielaufruf jeder Funktion]

Im folgenden Absatz werden die Schritte des Chatbots ausgeführt.

## Definitionen Preprocessing

Bla...

Notes
- Unabhängig der Anzahl ihrer Sätze, soll in jeder Nachricht nicht mehr als eine Aufgabe/ein Task erkannt werden. Sonst ist es kaum möglich, die in der Nachricht enthaltenen Informationen präzise zuzuordnen und konkrete Rückfragen zu fehlenden Angaben zu stellen.
- Zudem kann nicht vorausgesetzt werden, dass die Nachrichten der User immer mit den Regeln der Interpunktion konform sind.  
- Da Regeln der Orthographie bzw. Interpunktion in der Chat-Kommunikation oftmals vernachlässigt werden, sollen die Tokens je Nachricht auf Wortebene ermittelt und Satzzeichen vollständig ignoriert werden

- NLTK verfügt über eine POS-Tagging-Funktion namens ```pos_tag```, die derzeit jedoch nur Englisch und Russisch unterstützt (siehe https://www.nltk.org/api/nltk.tag.pos_tag.html).
- Da der Chat auf Deutsch stattfinden soll, haben wir uns für den *Hanover Tagger* (kurz *HanTa*) von Christian Wartena von der Hochschule Hannover entschieden, der Funktionen sowohl zum POS-Tagging als auch zum Lemmatisieren von Tokens in deutscher Sprache bietet (siehe https://github.com/wartaal/HanTa und https://serwiss.bib.hs-hannover.de/frontdoor/index/index/docId/2457).
- Da das Model mit dem TIGER Corpus trainiert wurde, entsprechen die POS-Tags weitestgehend denen des Korpus bzw. dem Stuttgart-Tübingen-Tagset (STTS) (siehe https://www.ims.uni-stuttgart.de/forschung/ressourcen/lexika/germantagsets/#id-cfcbf0a7-0)



- Ausgabe Objekt mit
{ 
  "original" : "Bla",
  "corrected" : "Bla",
  "lemma": "Bla",
  "pos": "Bla",
  "ner": ""
}
- ACHTUNG: STOPWORDS ENTFERNEN TOKENS



## Definitionen Intent-Matching

Bla...


In der Methode "get_response" wird der Text der Anfrage übergeben. Bei diesem Text werden dann die oben aufgeführten einzelnen Schritte durchgeführt. Dadurch wird eine Antwort ausgewählt und eventuelle weitere Bearbeitungsschritte angestoßen. Die Antwort wird von der Methode "get_response" zurückgegeben.
```
Code chatbot.py
```

## Definitionen Regelwerk

Bla.. 

Notes
- Die getaggten Tokens sind primär für die Erkennung des Intents relevant
- Damit die ursprüngliche Satzstruktur analysiert werden kann und Personen-, Prüfungs-, Straßen- oder Ortsnamen von der Rechtschreibkorrektur und Lemmatisierung unberührt bleiben, wird der Funktion zum Auswerten der für einen Task relevanten Informationen auch der Originaltext der Nachricht übergeben.
- TO DO: BESSER TOKENS ALS OBJEKTE INKL. ORIGINAL?


## Chatbot Hauptmodul 

Bla...

Notes
- Hier werden alle Schritte miteinander verknüpft
- Ort der Ein- und Ausgabe von Nachrichten 

    

## GUI/Frontend (optional)

**Im Jupyter-Notebook wird es kein Frontend geben, daher wären wir an dieser Stelle fertig (im Notebook muss der Code in chatbot.py minimal abgeändert werden, damit die Terminal-Eingabe wieder da ist).**

Notes
- Flask zum Austausch von User-Nachrichten und Chatbot-Antworten zwischen Server und Web-Frontend
- ...


