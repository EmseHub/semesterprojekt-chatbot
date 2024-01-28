
from datetime import datetime
import re

from rule_engine.data_service import students, courses
from rule_engine.helpers import get_random_item_in_list


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
def process_task(state_running_task, tagged_tokens, intent):
    '''Ermittlung des auszuführenden Tasks & Initiierung der Funktion'''

    # Auf ursprünglichen Task zurückfallen, falls sich kein neuer Task ergibt
    new_state_running_task = state_running_task
    response = None
    is_data_changed = False

    # Leere Eingabe, kein Intent ermittelt --> kein Task ausführbar
    if not tagged_tokens:
        return (new_state_running_task, response, is_data_changed)

    # Prozess anstoßen, falls noch ein Task vorliegt oder für den Intent vorgesehen ist
    if (state_running_task or intent["task"]):
        if not state_running_task:
            state_running_task = {"name": intent.task, "params": {}}

        running_task_name = state_running_task["name"]

        response = f'Für die Aufgabe "{
            running_task_name}" ist leider noch kein Ablauf definiert...'

        intent_tag = intent["tag"]

        # Funktion/Prozess für den entsprechenden Task auswählen
        new_state_running_task, response, is_data_changed = (lambda: (
            {
                'adresse_aendern': process_task_adresse_aendern,
                'nachname_aendern': process_task_nachname_aendern,
                'pruefung_anmelden': process_task_pruefung_anmelden,
                'pruefung_abmelden': process_task_pruefung_abmelden,
                'pruefung_status': process_task_pruefung_status
            }.get(running_task_name, lambda *args: [None, response, is_data_changed])
        )(state_running_task, tagged_tokens, intent_tag))()

        # Task abgeschlossen oder abgebrochen --> Anschlussfrage ergänzen
        if not state_running_task:
            response += ' ' + get_random_item_in_list([
                'Kann ich sonst noch etwas für Dich tun?',
                'Darf es sonst noch etwas sein?',
                'Hast Du weitere Anliegen?'
            ])

    # Kein Task für den Intent erforderlich --> Antwort auswählen
    else:
        response = get_random_item_in_list(intent["responses"])

    return (new_state_running_task, response, is_data_changed)


# ADRESSE ÄNDERN
def process_task_adresse_aendern(state_running_task, tagged_tokens, intent_tag):
    is_data_changed = False

    if intent_tag == 'ablehnung':
        return [None, 'Ich breche die Adressänderung ab.', is_data_changed]

    if not state_running_task or not tagged_tokens or not tagged_tokens.strip():
        return [state_running_task, None, is_data_changed]

    # Daten in Nachricht erkennen
    # TODO: Funktion get_missing_student_information() implementieren
    obj_detected_data, str_query = get_missing_student_or_address_from_message(
        {**state_running_task.params}, tagged_tokens
    )
    state_running_task.params = obj_detected_data

    # Prüfen, ob alle Daten vorliegen
    # Staat außen vor da erstmal nur Deutschland
    arr_address_keys = ['strasse', 'hausnr', 'stadt', 'plz']
    if not (
        obj_detected_data.objStudent
        or obj_detected_data.objAddress
        or any(not obj_detected_data.objAddress[key] for key in arr_address_keys)
    ):
        return [state_running_task, str_query, is_data_changed]

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if intent_tag != 'zustimmung':
        str_response = (
            f'Nun denn, {obj_detected_data.objStudent.vorname.split(
                " ")[0]}, ich ändere Deine Adresse zu "{obj_detected_data.objAddress.strasse} '
            f'{obj_detected_data.objAddress.hausnr}, {obj_detected_data.objAddress.plz} {
                obj_detected_data.objAddress.stadt}", okay?'
        )
        return [state_running_task, str_response, is_data_changed]

    # Vorgang bestätigt --> Daten ändern und Running Task zurücksetzen

    # Prüfen, ob der richtige Student erkannt wurde (wurde zuvor bereits die richtige Matr.Nr. genannt)
    obj_aktueller_student = next(
        (s for s in students if s.matnr == obj_detected_data.objStudent.matnr), None)
    if obj_aktueller_student:
        obj_aktueller_student.adresse = {**obj_detected_data.objAddress}
        obj_aktueller_student.letztesUpdate = datetime.datetime.now().isoformat()
        is_data_changed = True

    return [None, 'Vielen Dank, die Adresse wurde geändert.', is_data_changed]


# NACHNAME ÄNDERN
def process_task_nachname_aendern(state_running_task, tagged_tokens, intent_tag):
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
    arr_address_keys = ['vorname', 'nachname']
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
        obj_student_live.letztesUpdate = datetime.datetime.now().isoformat()
        is_data_changed = True

    return [None, 'Vielen Dank, dein Nachname wurde geändert.', is_data_changed]


# PRÜFUNG ANMELDEN
def process_task_pruefung_anmelden(state_running_task, tagged_tokens, intent_tag):
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
def process_task_pruefung_abmelden(state_running_task, tagged_tokens, intent_tag):
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
def process_task_pruefung_status(state_running_task, tagged_tokens, intent_tag):
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
