import re
from helpers import get_random_item_in_list


def process_task(state_running_task, tagged_tokens, intent):

    new_state_running_task = state_running_task
    response = None
    is_data_changed = False

    if not tagged_tokens:
        return (new_state_running_task, response, is_data_changed)

    if (state_running_task or intent["task"]):
        if not state_running_task:
            state_running_task = {"name": intent.task, "params": {}}

        running_task_name = state_running_task["name"]

        response = f'Für die Aufgabe "{
            running_task_name}" ist leider noch kein Ablauf definiert...'

        intent_tag = intent["tag"]

        # TODO Bitte Beschreibung mit Erläuterung hinzufügen, was genau passiert hier?
        # vermutlich Auswahl des durchzuführenden Tasks... aber durch lambda etwas unklar
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
    else:
        response = get_random_item_in_list(intent["responses"])

    return (new_state_running_task, response, is_data_changed)


def process_task_adresse_aendern(state_running_task, tagged_tokens, intent_tag):
    return (None, None, None)


def process_task_nachname_aendern(state_running_task, tagged_tokens, intent_tag):
    return (None, None, None)


def process_task_pruefung_anmelden(state_running_task, tagged_tokens, intent_tag):
    return (None, None, None)


def process_task_pruefung_abmelden(state_running_task, tagged_tokens, intent_tag):
    return (None, None, None)


def process_task_pruefung_status(state_running_task, tagged_tokens, intent_tag):
    return (None, None, None)
