# Feedback zum aktuellen Zwischenstand/Code


## Code Lesbarkeit
### Beschreibung & Benennung
- Beschreibung von Funktionen & Variablen fehlt noch (für Nachvollziehbarkeit beim Lesen von fremden Code, Erklärung Popup beim Hovern über Variable/Funktion on-the-fly hilft sehr)
- viele Variablennamen sind sehr ähnlich benannt und lang (Bsp. state_running_task, new_state_running_task, running_task_name, ...)
  - schwer zu lesen und auseinander zu halten
  - auch in Schleifen manchmal schwer nachvollziehbar
- vor allem bei Nutzung von verschachtelten/abgekürzten lambda Funktionen bitte etwas beschreiben, was da genau passiert (siehe auch #TODO Tag)

## Aufbau/Dateien
- rules.py =/= Regeln sondern Abarbeitung von Tasks/Processes (evtl. umbenennen? Als Ordner/Modulname aber fine)

## Funktionalität
### Intent Matching
- Schlagwort-Treffer System gefällt mir soweit gut, aber ich sehe mögliche Probleme:
  - wenn ein Nutzer Trash eingibt, der aber zwei passende Stichwörter eines Intents enthält, wird ggf. falscher Task ausgewählt und danach gefragt
  - z.B. "anpassen ändern asdf qwertz blaaaizusdfgasdifzgv" 
    - --> Ergebnis: zwei gefundene Intents: adresse_aendern / nachname_aendern
    - die beiden Optionen werden als Liste "possible_intents" gespeichert
    - max(list) kann aber kein Maximum als finalen Intent ermitteln, denn beide Intents des haben hit_count = 2
    - --> welcher wird nun ausgewählt?