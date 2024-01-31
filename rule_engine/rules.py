from operator import itemgetter
from datetime import datetime
import re


from rule_engine.data_service import students, courses
from rule_engine.helpers import get_random_item_in_list, replace_diacritics

from rule_engine.entity_detection import detect_student_in_message, detect_course_in_message, detect_address_in_message


# region     --------------------------- Daten ermitteln ---------------------------


def get_missing_student_information(current_task: str, message: str):
    '''[Prototyp Alternative] Zusammengeführte Funktion zum Abfragen aller fehlenden Informationen
    : Erfragt fehlende Informationen vom Studenten und gibt diese als Dictionary zurück.
    : 
    '''
    result = {}

    # ermitteln, welche Informationen fehlen/abgefragt werden sollen
    match current_task:
        case "adresse_aendern":
            # todo
            result = {}
        case "nachname_aendern":
            # todo
            result = {}
        case "pruefung_status":
            # todo
            result = {}
        case "pruefung_anmelden":
            # todo
            result = {}
        case "pruefung_abmelden":
            # todo
            result = {}

    return result


def get_missing_student_or_address_from_message():
    '''Fehlende Informationen (Matrikelnummer oder Adresse) vom Studenten abfragen. 
    '''
    return None

# endregion  --------------------------- Daten ermitteln ---------------------------


# region --------------------------- Task-Funtkionen ---------------------------

# TASK WÄHLEN
def process_task(state_running_task, tagged_tokens, message_raw, intent):
    '''Ermittlung des auszuführenden Tasks & Initiierung der Funktion'''

    # Auf ursprünglichen Task zurückfallen, falls sich kein neuer Task ergibt
    new_state_running_task = state_running_task
    response = None
    is_data_changed = False

    # Leere Eingabe, keine Tokens ermittelt
    if (not tagged_tokens or not message_raw):
        return (state_running_task, response, is_data_changed)

    message_raw_simple = re.sub(r"\s+", " ", message_raw).strip()
    message_processed = replace_diacritics(message_raw_simple.lower())

    # Prüfen, ob es noch entweder noch einen offenen Task gibt, oder die Eröffnung eines neuen aus dem Intent hervorgeht
    if (state_running_task or intent.get("task")):
        if not state_running_task:
            state_running_task = {"name": intent.get("task"), "params": {}}

        running_task_name = state_running_task.get("name")

        response = f'Für die Aufgabe "{
            running_task_name}" ist leider noch kein Ablauf definiert...'

        intent_tag = intent["tag"]

        if (running_task_name == "adresse_aendern"):
            state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
                process_task_adresse_aendern(
                    state_running_task, message_raw_simple, message_processed, intent_tag
                )
            )
            # print(
            #     next((s for s in students if (s["matnr"] == "1234567")), None)
            # )

        elif (running_task_name == "nachname_aendern"):
            state_running_task, response, is_data_changed = process_task_nachname_aendern(
                state_running_task, tagged_tokens,  message_raw_simple, intent_tag
            )
        elif (running_task_name == "pruefung_anmelden"):
            state_running_task, response, is_data_changed = process_task_pruefung_anmelden(
                state_running_task, tagged_tokens,  message_raw_simple, intent_tag
            )
        elif (running_task_name == "pruefung_abmelden"):
            state_running_task, response, is_data_changed = process_task_pruefung_abmelden(
                state_running_task, tagged_tokens,  message_raw_simple, intent_tag
            )
        elif (running_task_name == "pruefung_status"):
            state_running_task, response, is_data_changed = process_task_pruefung_status(
                state_running_task, tagged_tokens,  message_raw_simple, intent_tag
            )
        else:
            state_running_task, response, is_data_changed = (
                None, response, is_data_changed)

        # Funktion/Prozess für den entsprechenden Task auswählen
        # state_running_task, response, is_data_changed = (lambda: (
        #     {
        #         "adresse_aendern": process_task_adresse_aendern,
        #         "nachname_aendern": process_task_nachname_aendern,
        #         "pruefung_anmelden": process_task_pruefung_anmelden,
        #         "pruefung_abmelden": process_task_pruefung_abmelden,
        #         "pruefung_status": process_task_pruefung_status
        #     }.get(running_task_name, lambda *args: [None, response, is_data_changed])
        # )(state_running_task, tagged_tokens, message_raw_simple, intent_tag))()

        # # Task abgeschlossen oder abgebrochen --> Anschlussfrage ergänzen
        # if not state_running_task:
        #     response += " " + get_random_item_in_list([
        #         "Kann ich sonst noch etwas für Dich tun?",
        #         "Darf es sonst noch etwas sein?",
        #         "Hast Du weitere Anliegen?"
        #     ])

    # Es läuft kein Taskt oKein Task für den Intent erforderlich --> Antwort auswählen
    else:
        response = get_random_item_in_list(intent["responses"])

    # return (state_running_task, response, is_data_changed)
    return {"state_running_task": state_running_task, "response": response, "is_data_changed": is_data_changed}


# ADRESSE ÄNDERN
def process_task_adresse_aendern(state_running_task, message_raw, message_processed, intent_tag):
    if (not state_running_task or not message_raw or not message_processed or not intent_tag):
        return {"state_running_task": None, "response": None, "is_data_changed": False}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Adressänderung ab.", "is_data_changed": False}

    # Was bisher an Werten für die Erledigung des Tasks ermittelt wurde
    student = state_running_task["params"].get("student")
    address = state_running_task["params"].get("address")

    # String mit Rückfragen bei unvollständigen Angaben
    query = ""

    # Falls dem Task noch kein Student zugeordnet wurde, versuche diesen anhand einer Matrikelnummer im Text zu ermitteln
    if (not student):
        student, query_student = itemgetter("student", "query")(
            detect_student_in_message(message_processed)
        )
        query = query_student

    # Angaben, die eine Adresse aufweisen muss
    address_keys = ["strasse", "hausnr", "stadt", "plz"]

    # Falls dem Task noch keine vollständige neue Adresse zugeordnet wurde, versuche diese dem Text zu entnehmen
    if (not address or any(not address.get(key) for key in address_keys)):
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

    # Da, alle Daten vorhanden und Vorgang bestätigt, kann Datensatz nun in DB aktualisert und Running Task zurückgesetzt werden
    student = next(
        (s for s in students if (s["matnr"] == student["matnr"])), student
    )
    student["adresse"] = {**address}
    student["letztesUpdate"] = datetime.now().isoformat()

    return {"state_running_task": None, "response": "Vielen Dank, die Adresse wurde geändert.", "is_data_changed": True}


# NACHNAME ÄNDERN
def process_task_nachname_aendern(state_running_task, tagged_tokens, message, intent_tag):
    is_data_changed = False

    if intent_tag == 'ablehnung':
        return [None, 'Ich breche die Nachnamensänderung ab.', is_data_changed]

    if not state_running_task or not tagged_tokens or not tagged_tokens.strip():
        return [state_running_task, None, is_data_changed]

    # Daten in Nachricht erkennen
    obj_detected_data, str_query = get_missing_student_or_address_from_message(
        {**state_running_task.params}, tagged_tokens
    )
    state_running_task.params = obj_detected_data

    # Prüfen, ob alle Daten vorliegen
    address_keys = ['vorname', 'nachname']
    if not (
        obj_detected_data.objStudent
    ):
        return [state_running_task, str_query, is_data_changed]

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if intent_tag != 'zustimmung':
        str_response = (
            f'Nun denn, {obj_detected_data.objStudent.vorname.split(" ")[0]}, ich ändere Deinen Nachnamen zu "{
                obj_detected_data.objStudent.nachname}", okay?'
        )
        return [state_running_task, str_response, is_data_changed]

    # Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen
    obj_student_live = next(
        (s for s in students if s.matnr == obj_detected_data.objStudent.matnr), None)
    if obj_student_live:
        obj_student_live.nachname = {**obj_detected_data.objStudent}
        obj_student_live.letztesUpdate = datetime.now().isoformat()
        is_data_changed = True

    return [None, 'Vielen Dank, dein Nachname wurde geändert.', is_data_changed]


# PRÜFUNG ANMELDEN
def process_task_pruefung_anmelden(state_running_task, tagged_tokens, message, intent_tag):
    is_data_changed = False

    if intent_tag == 'ablehnung':
        return [None, 'Ich breche die Prüfungsanmeldung ab.', is_data_changed]

    if not state_running_task or not tagged_tokens or not tagged_tokens.strip():
        return [state_running_task, None, is_data_changed]

    # Prüfen, ob Anhand der Nachricht und ggf. bisheriger Angaben die referenzierte Prüfung ermittelt werden kann
    obj_existing_pruefung, obj_task_state_params, str_query = get_referenced_pruefung_from_message(
        {**state_running_task.params}, tagged_tokens
    )
    state_running_task.params = obj_task_state_params
    obj_student, obj_course = obj_task_state_params['objStudent'], obj_task_state_params['objCourse']

    # Prüfen, ob die notwendigen Daten zu User und Kurs vorliegen
    if not obj_student or not obj_course:
        return [state_running_task, str_query, is_data_changed]

    # Prüfen, ob Kurs dem User bereits zugeordnet ist, und wenn ja, ob die Prüfung noch nicht bestanden und noch nicht angemeldet ist
    if obj_existing_pruefung:
        if obj_existing_pruefung['note'] is not None:
            str_response = f"{obj_student['vorname'].split(' ')[0]}, Du hast die Prüfung im Fach \"{
                obj_course['name']}\" bereits mit der Note {obj_existing_pruefung['note']:.1f} bestanden."
            return [None, str_response, is_data_changed]

        if obj_existing_pruefung['isAngemeldet']:
            str_response = f"{obj_student['vorname'].split(' ')[0]}, die Prüfung im Fach \"{
                obj_course['name']}\" ist bereits angemeldet."
            return [None, str_response, is_data_changed]

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if intent_tag != 'zustimmung':
        str_response = f"Okay {obj_student['vorname'].split(' ')[0]}, möchtest Du die Prüfung im Fach \"{
            obj_course['name']}\" bei {obj_course['lehrperson']} verbindlich anmelden?"
        return [state_running_task, str_response, is_data_changed]

    # Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen
    obj_student_live = next(
        (s for s in students if s['matnr'] == obj_student['matnr']), None)
    if obj_existing_pruefung:
        next(p for p in obj_student_live['pruefungen'] if p['kursID'] == obj_course['id'])[
            'isAngemeldet'] = True
    else:
        obj_new_pruefung = {
            'kursID': obj_course['id'], 'isAngemeldet': True, 'note': None}
        obj_student_live['pruefungen'].append(obj_new_pruefung)

    obj_student_live['letztesUpdate'] = datetime.now().isoformat()
    is_data_changed = True

    return [None, 'Die Prüfung wurde erfolgreich angemeldet.', is_data_changed]


# PRÜFUNG ABMELDEN
def process_task_pruefung_abmelden(state_running_task, tagged_tokens, message, intent_tag):
    is_data_changed = False

    if intent_tag == 'ablehnung':
        return [None, 'Ich stoppe die Abmeldung der Prüfung.', is_data_changed]

    if not state_running_task or not tagged_tokens or not tagged_tokens.strip():
        return [state_running_task, None, is_data_changed]

    # Prüfen, ob Anhand der Nachricht und ggf. bisheriger Angaben die referenzierte Prüfung ermittelt werden kann
    obj_existing_pruefung, obj_task_state_params, str_query = get_referenced_pruefung_from_message(
        {**state_running_task.params}, tagged_tokens
    )
    state_running_task.params = obj_task_state_params
    obj_student, obj_course = obj_task_state_params['objStudent'], obj_task_state_params['objCourse']

    # Prüfen, ob die notwendigen Daten zu User und Kurs vorliegen
    if not obj_student or not obj_course:
        return [state_running_task, str_query, is_data_changed]

    # Prüfen, ob der Kurs dem User zugeordnet und die Prüfung angemeldet ist
    if not obj_existing_pruefung or not obj_existing_pruefung['isAngemeldet']:
        str_response = (
            f"{obj_student['vorname'].split(' ')[0]}, Du kannst die Prüfung im Fach \"{
                obj_course['name']}\" nicht abmelden, "
            "da Du gar nicht angemeldet bist."
        )
        return [None, str_response, is_data_changed]

    # Prüfen, ob der Kurs noch nicht bestanden ist
    if obj_existing_pruefung['note'] is not None:
        str_response = (
            f"{obj_student['vorname'].split(' ')[0]}, Du kannst die Prüfung im Fach \"{
                obj_course['name']}\" nicht abmelden, "
            f"da Du sie bereits mit der Note {
                obj_existing_pruefung['note']:.1f} bestanden hast."
        )
        return [None, str_response, is_data_changed]

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if intent_tag != 'zustimmung':
        str_response = (
            f"Okay {obj_student['vorname'].split(' ')[0]}, möchtest Du die Prüfung im Fach \"{
                obj_course['name']}\" "
            f"bei {obj_course['lehrperson']} wirklich abmelden?"
        )
        return [state_running_task, str_response, is_data_changed]

    # Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen
    obj_student_live = next(
        (s for s in students if s['matnr'] == obj_student['matnr']), None)
    next(p for p in obj_student_live['pruefungen'] if p['kursID'] == obj_course['id'])[
        'isAngemeldet'] = False
    obj_student_live['letztesUpdate'] = datetime.now().isoformat()
    is_data_changed = True

    return [None, 'Die Prüfung wurde erfolgreich abgemeldet.', is_data_changed]


# PRÜFUNGSSTATUS ABFRAGEN
def process_task_pruefung_status(state_running_task, tagged_tokens, message, intent_tag):
    is_data_changed = False

    if intent_tag == 'ablehnung':
        return [None, 'Ich stoppe die Statusabfrage der Prüfung.', is_data_changed]

    if not state_running_task or not tagged_tokens or not tagged_tokens.strip():
        return [state_running_task, None, is_data_changed]

    # Prüfen, ob Anhand der Nachricht und ggf. bisheriger Angaben die referenzierte Prüfung ermittelt werden kann
    obj_existing_pruefung, obj_task_state_params, str_query = get_referenced_pruefung_from_message(
        {**state_running_task.params}, tagged_tokens
    )
    state_running_task.params = obj_task_state_params
    obj_student, obj_course = obj_task_state_params['objStudent'], obj_task_state_params['objCourse']

    # Prüfen, ob die notwendigen Daten zu User und Kurs vorliegen
    if not obj_student or not obj_course:
        return [state_running_task, str_query, is_data_changed]

    # Annahme, dass der Kurs angemeldet ist
    str_response = (
        f"{obj_student['vorname'].split(' ')[0]}, die Prüfung im Fach \"{
            obj_course['name']}\" ist angemeldet und noch nicht bestanden."
    )

    # Prüfen, ob der Kurs wirklich dem User zugeordnet und die Prüfung angemeldet ist
    if not obj_existing_pruefung or not obj_existing_pruefung['isAngemeldet']:
        str_response = (
            f"{obj_student['vorname'].split(' ')[0]}, die Prüfung im Fach \"{
                obj_course['name']}\" ist weder angemeldet noch bestanden."
        )
    # Prüfen, ob der Kurs bestanden ist
    elif obj_existing_pruefung['note'] is not None:
        str_response = (
            f"Glückwunsch {obj_student['vorname'].split(' ')[0]}, Du hast die Prüfung im Fach \"{
                obj_course['name']}\" "
            f"mit der Note {obj_existing_pruefung['note']:.1f} bestanden."
        )

    return [None, str_response, is_data_changed]


# endregion --------------------------- Task-Funtkionen ---------------------------
