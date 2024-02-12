from operator import itemgetter
from datetime import datetime
import re

from rule_engine.data_service import students, courses
from rule_engine.helpers import get_random_item_in_list, replace_diacritics
from rule_engine.entity_detection import detect_student_in_message, detect_course_in_message, detect_address_in_message, detect_new_surname_in_message


# region --------------------------- Task-Funtkionen ---------------------------
def supply_pruefung_data(state_running_task, message_processed):
    """Generische Hilfsfunktion zur Ermittlung der Informationen einer Prüfung (Kurs und Student) und dem Prüfungsobjekt selbst."""

    if (not state_running_task or not message_processed):
        return {"state_running_task": state_running_task, "response": None, "is_data_changed": False}

    # Was bisher an Werten für die Zuordnung einer Prüfung ermittelt wurde
    student = state_running_task["params"].get("student")
    course = state_running_task["params"].get("course")

    # String mit Rückfragen bei unvollständigen Angaben
    query = ""

    # Falls dem Task noch kein Student zugeordnet wurde, versuche, diesen anhand einer Matrikelnummer im Text zu ermitteln
    if (not student):
        student, query_student = itemgetter("student", "query")(
            detect_student_in_message(message_processed)
        )
        query = query_student

    # Falls dem Task noch kein Kurs zugeordnet wurde, versuche, diesen dem Text zu entnehmen
    if (not course):
        course, query_course = itemgetter("course", "query")(
            detect_course_in_message(message_processed)
        )
        query += (" " + query_course)

    state_running_task["params"]["student"] = student
    state_running_task["params"]["course"] = course
    query = query.strip()

    # Falls alle relevanten Daten vorhanden sind, prüfen, ob dem Student bereits eine Prüfung in diesem Kurs zugeordnet ist
    exam = None if (not student or not course) else next(
        (pruefung for pruefung in student["pruefungen"] if (
            pruefung["kursID"] == course["id"]
        )), None
    )
    return {"state_running_task": state_running_task, "exam": exam, "query": query}


def adresse_aendern(state_running_task, message_raw, message_processed, intent_tag):
    if (not state_running_task or not message_raw or not message_processed or not intent_tag):
        return {"state_running_task": state_running_task, "response": None, "is_data_changed": False}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Adressänderung ab.", "is_data_changed": False}

    # Was bisher an Werten für die Erledigung des Tasks ermittelt wurde
    student = state_running_task["params"].get("student")
    address = state_running_task["params"].get("address")

    # String mit Rückfragen bei unvollständigen Angaben
    query = ""

    # Falls dem Task noch kein Student zugeordnet wurde, versuche, diesen anhand einer Matrikelnummer im Text zu ermitteln
    if (not student):
        student, query_student = itemgetter("student", "query")(
            detect_student_in_message(message_processed)
        )
        query = query_student

    # Angaben, die eine Adresse aufweisen muss
    address_keys = ["strasse", "hausnr", "stadt", "plz"]

    # Falls dem Task noch keine vollständige neue Adresse zugeordnet wurde, versuche, diese dem Text zu entnehmen
    if (not address or not all(address.get(key) for key in address_keys)):
        address, query_address = itemgetter("address", "query")(
            detect_address_in_message(address, message_raw)
        )
        query += (" " + query_address)

    state_running_task["params"]["student"] = student
    state_running_task["params"]["address"] = address
    query = query.strip()

    # Prüfen, ob noch Rückfragen vorliegen, oder alle relevanten Daten vorhanden sind
    if (query):
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (intent_tag != "zustimmung"):
        query = (
            f'Nun denn, {student["vorname"].split()[0]}, ich ändere Deine Adresse zu "{
                address["strasse"]} {address["hausnr"]}, {address["plz"]} {address["stadt"]}", okay?'
        )
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Prüfen, ob die neue Adresse der bisherigen entspricht
    if (all(address.get(key) == student.get("adresse").get(key) for key in address_keys)):
        return {"state_running_task": None, "response": "Diese Anschrift ist bereits in unserem System hinterlegt, daher beende ich den Vorgang.", "is_data_changed": False}

    # Da, alle Daten vorhanden und Vorgang bestätigt, kann Datensatz nun in DB aktualisert und Running Task zurückgesetzt werden
    student = next(
        (s for s in students if (s["matnr"] == student["matnr"])), student
    )
    student["adresse"] = {**address}
    student["letztesUpdate"] = datetime.now().isoformat()

    return {"state_running_task": None, "response": "Vielen Dank, die Adresse wurde geändert.", "is_data_changed": True}


def nachname_aendern(state_running_task, tagged_tokens, message_raw, message_processed, intent_tag):
    if (not state_running_task or not tagged_tokens or not message_raw or not message_processed or not intent_tag):
        return {"state_running_task": state_running_task, "response": None, "is_data_changed": False}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Namensänderung ab.", "is_data_changed": False}

    # Falls dem Task noch kein Student zugeordnet wurde, versuche, diesen anhand einer Matrikelnummer im Text zu ermitteln
    student = state_running_task["params"].get("student")
    if (not student):
        student, query_student = itemgetter("student", "query")(
            detect_student_in_message(message_processed)
        )
        if (not student):
            return {"state_running_task": state_running_task, "response": query_student, "is_data_changed": False}
        state_running_task["params"]["student"] = student

    # Falls dem Task noch kein neuer Nachname zugeordnet wurde, versuche, diese dem Text zu entnehmen
    surname = state_running_task["params"].get("surname")
    if (not surname):
        surname, query_surname = itemgetter("surname", "query")(
            detect_new_surname_in_message(student, tagged_tokens, message_raw)
        )
        if (not surname):
            return {"state_running_task": state_running_task, "response": query_surname, "is_data_changed": False}
        state_running_task["params"]["surname"] = surname

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (intent_tag != "zustimmung"):
        query = (
            f'Alles klar, {student["vorname"].split()[0]}, ich ändere Deinen Nachnamen dann um in "{
                surname}". Ist das so korrekt?'
        )
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Prüfen, ob der neue Nachname dem bisherigen entspricht
    if (student.get("nachname") == surname):
        return {"state_running_task": None, "response": "Witzbold! Genau dieser Nachname ist im System hinterlegt, daher breche ich den Vorgang ab.", "is_data_changed": False}

    # Da, alle Daten vorhanden und Vorgang bestätigt, kann Datensatz nun in DB aktualisert und Running Task zurückgesetzt werden
    student = next(
        (s for s in students if (s["matnr"] == student["matnr"])), student
    )
    student["nachname"] = surname
    student["letztesUpdate"] = datetime.now().isoformat()

    return {"state_running_task": None, "response": "Vielen Dank, Dein Nachname wurde aktualisiert.", "is_data_changed": True}


def pruefung_anmelden(state_running_task, message_processed, intent_tag):
    if (not state_running_task or not message_processed or not intent_tag):
        return {"state_running_task": state_running_task, "response": None, "is_data_changed": False}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Prüfungsanmeldung ab.", "is_data_changed": False}

    # Angaben zu Student und Kurs ermitteln und zugehörige Prüfung aus DB auslesen
    state_running_task, exam, query, = itemgetter("state_running_task", "exam", "query")(
        supply_pruefung_data(state_running_task, message_processed)
    )

    # Prüfen, ob noch Rückfragen vorliegen, oder alle relevanten Daten vorhanden sind
    if (query):
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Ermittelte Angaben in Hilfsvariablen speichern
    student = state_running_task["params"].get("student")
    course = state_running_task["params"].get("course")

    # Falls bei Student bereits eine Prüfung vorhanden ist, sicherstellen, dass diese noch nicht bestanden und nocht nicht angemeldet ist
    if (exam):
        if (not (exam["note"] is None)):
            response = f'{student["vorname"].split()[0]}, Du hast die Prüfung im Fach "{course["name"]}" bereits mit der Note {
                "{:.1f}".format(exam["note"])} bestanden.'
            return {"state_running_task": None, "response": response, "is_data_changed": False}

        if (exam["isAngemeldet"]):
            response = f'{student["vorname"].split()[0]}, die Prüfung im Fach "{
                course["name"]}" ist bereits angemeldet.'
            return {"state_running_task": None, "response": response, "is_data_changed": False}

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (intent_tag != "zustimmung"):
        query = f'Okay {student["vorname"].split()[0]}, möchtest Du die Prüfung im Fach "{
            course["name"]}" bei {course["lehrperson"]} verbindlich anmelden?'
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Da, alle Daten vorhanden und Vorgang bestätigt, kann Datensatz nun in DB aktualisert und Running Task zurückgesetzt werden
    student = next(
        (s for s in students if (s["matnr"] == student["matnr"])), student
    )
    if (exam):
        next(
            pruefung for pruefung in student["pruefungen"] if pruefung["kursID"] == course["id"]
        )["isAngemeldet"] = True
    else:
        exam = {"kursID": course["id"], "isAngemeldet": True, "note": None}
        student["pruefungen"].append(exam)

    student["letztesUpdate"] = datetime.now().isoformat()

    return {"state_running_task": None, "response": "Die Prüfung wurde erfolgreich angemeldet.", "is_data_changed": True}


def pruefung_abmelden(state_running_task, message_processed, intent_tag):
    if (not state_running_task or not message_processed or not intent_tag):
        return {"state_running_task": state_running_task, "response": None, "is_data_changed": False}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Abmeldung der Prüfung ab.", "is_data_changed": False}

    # Angaben zu Student und Kurs ermitteln und zugehörige Prüfung aus DB auslesen
    state_running_task, exam, query, = itemgetter("state_running_task", "exam", "query")(
        supply_pruefung_data(state_running_task, message_processed)
    )

    # Prüfen, ob noch Rückfragen vorliegen, oder alle relevanten Daten vorhanden sind
    if (query):
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Ermittelte Angaben in Hilfsvariablen speichern
    student = state_running_task["params"].get("student")
    course = state_running_task["params"].get("course")

    # Prüfen, ob dem Studenten eine Prüfung in diesem Kurs zugeordnet ist und ob diese angemeldet ist
    if (not exam or not exam["isAngemeldet"]):
        response = f'{student["vorname"].split()[0]}, Du kannst die Prüfung im Fach "{
            course["name"]}" nicht abmelden, da Du gar nicht angemeldet bist.'
        return {"state_running_task": None, "response": response, "is_data_changed": False}

    # Prüfen, ob der Kurs bereits bestanden ist
    if (not (exam["note"] is None)):
        response = (
            f'{student["vorname"].split()[0]}, Du kannst die Prüfung im Fach "{
                course["name"]}" nicht abmelden, da Du sie bereits mit der Note {"{:.1f}".format(exam["note"])} bestanden hast.'
        )
        return {"state_running_task": None, "response": response, "is_data_changed": False}

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (intent_tag != "zustimmung"):
        query = f'Okay {student["vorname"].split()[0]}, möchtest Du die Prüfung im Fach "{
            course["name"]}" bei {course["lehrperson"]} wirklich abmelden?'
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Da, alle Daten vorhanden und Vorgang bestätigt, kann Datensatz nun in DB aktualisert und Running Task zurückgesetzt werden
    student = next(
        (s for s in students if (s["matnr"] == student["matnr"])), student
    )
    next(
        pruefung for pruefung in student["pruefungen"] if pruefung["kursID"] == course["id"]
    )["isAngemeldet"] = False

    student["letztesUpdate"] = datetime.now().isoformat()

    return {"state_running_task": None, "response": "Die Prüfung wurde erfolgreich abgemeldet.", "is_data_changed": True}


def pruefung_status(state_running_task, message_processed, intent_tag):
    if (not state_running_task or not message_processed or not intent_tag):
        return {"state_running_task": state_running_task, "response": None, "is_data_changed": False}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Abmeldung der Prüfung ab.", "is_data_changed": False}

    # Angaben zu Student und Kurs ermitteln und zugehörige Prüfung aus DB auslesen
    state_running_task, exam, query, = itemgetter("state_running_task", "exam", "query")(
        supply_pruefung_data(state_running_task, message_processed)
    )

    # Prüfen, ob noch Rückfragen vorliegen, oder alle relevanten Daten vorhanden sind
    if (query):
        return {"state_running_task": state_running_task, "response": query, "is_data_changed": False}

    # Ermittelte Angaben in Hilfsvariablen speichern
    student = state_running_task["params"].get("student")
    course = state_running_task["params"].get("course")

    # Response initialisieren mit der Annahme, dass der Kurs angemeldet ist
    response = f'{student["vorname"].split()[0]}, die Prüfung im Fach "{
        course["name"]}" ist angemeldet und noch nicht bestanden.'

    # Prüfen, ob dem Studenten eine Prüfung in diesem Kurs zugeordnet ist und ob diese angemeldet ist
    if (not exam or not exam["isAngemeldet"]):
        response = f'{student["vorname"].split()[0]}, die Prüfung im Fach "{
            course["name"]}" ist weder angemeldet noch bestanden.'

    # Prüfen, ob der Kurs (mit einer Note) bestanden ist
    elif (not (exam["note"] is None)):
        response = f'Glückwunsch {student["vorname"].split()[0]}, Du hast die Prüfung im Fach "{
            course["name"]}" mit der Note {"{:.1f}".format(exam["note"])} bestanden!'

    return {"state_running_task": None, "response": response, "is_data_changed": False}

# endregion --------------------------- Task-Funtkionen ---------------------------


# region --------------------------- Task-Steuerung ---------------------------
def process_task(state_running_task, tagged_tokens, message_raw, intent):
    '''Funktion, die die Fortsetzung eines bestehenden oder Eröffnung eines neu erkannten Tasks steuert. 
    Falls keine Ausgabe ausgeführt werden soll, wird ein simpler, im Intent vordefinierter Antwort-String zurückgegeben.'''

    response = None
    is_data_changed = False

    # Prüfen, ob eine Nachricht und Tokens vorhanden sind
    if (not tagged_tokens or not message_raw):
        return {"state_running_task": state_running_task, "response": response, "is_data_changed": is_data_changed}

    # Prüfen, ob es noch entweder noch einen offenen Task gibt, oder die Eröffnung eines neuen Tasks aus dem Intent hervorgeht
    if (state_running_task or intent.get("task")):

        if not state_running_task:
            state_running_task = {"name": intent.get("task"), "params": {}}

        running_task_name = state_running_task.get("name")

        response = f'Für die Aufgabe "{
            running_task_name}" ist leider noch kein Ablauf definiert...'

        message_raw_simple = re.sub(r"\s+", " ", message_raw).strip()
        message_processed = replace_diacritics(message_raw_simple.lower())
        intent_tag = intent["tag"]

        if (running_task_name == "adresse_aendern"):
            state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
                adresse_aendern(
                    state_running_task, message_raw_simple, message_processed, intent_tag
                )
            )
        elif (running_task_name == "nachname_aendern"):
            state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
                nachname_aendern(
                    state_running_task, tagged_tokens,  message_raw_simple, message_processed, intent_tag
                )
            )
        elif (running_task_name == "pruefung_anmelden"):
            state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
                pruefung_anmelden(
                    state_running_task, message_processed, intent_tag
                )
            )
        elif (running_task_name == "pruefung_abmelden"):
            state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
                pruefung_abmelden(
                    state_running_task, message_processed, intent_tag
                )
            )
        elif (running_task_name == "pruefung_status"):
            state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
                pruefung_status(
                    state_running_task, message_processed, intent_tag
                )
            )
        else:
            state_running_task, response, is_data_changed = (
                None, response, is_data_changed
            )

        # Funktion/Prozess für den entsprechenden Task auswählen
        # state_running_task, response, is_data_changed = (lambda: (
        #     {
        #         "adresse_aendern": adresse_aendern,
        #         "nachname_aendern": nachname_aendern,
        #         "pruefung_anmelden": pruefung_anmelden,
        #         "pruefung_abmelden": pruefung_abmelden,
        #         "pruefung_status": pruefung_status
        #     }.get(running_task_name, lambda *args: [None, response, is_data_changed])
        # )(state_running_task, tagged_tokens, message_raw_simple, intent_tag))()

        # Task abgeschlossen oder abgebrochen -> Anschlussfrage ergänzen
        if not state_running_task:
            response += " " + get_random_item_in_list([
                "Kann ich sonst noch etwas für Dich tun?",
                "Darf es sonst noch etwas sein?",
                "Hast Du weitere Anliegen?"
            ])

    # Es ist kein Task offen und soll auch kein neuer gestartet werden (Rückgabe eines im Intent vordefinierten Response-Strings)
    else:
        response = get_random_item_in_list(intent["responses"])

    # return (state_running_task, response, is_data_changed)
    return {"state_running_task": state_running_task, "response": response, "is_data_changed": is_data_changed}

# endregion --------------------------- Task-Steuerung ---------------------------
