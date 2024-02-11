import json
from operator import itemgetter

from preprocessing.preprocessing import get_tagged_tokens
from rule_engine.intent_matching import get_intent
from rule_engine.tasks import process_task

from rule_engine.data_service import students


def get_response(message, state_running_task, tagged_tokens):

    tagged_tokens = get_tagged_tokens(message)

    # diagnostic = tagged_tokens.copy()
    # print("---Diagnostic---\n", diagnostic)

    intent = get_intent(tagged_tokens)
    print("---Gefundener Intent---\n", intent.get("tag"))

    state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
        process_task(state_running_task, tagged_tokens, message, intent)
    )

    print("---Daten verändert---\n", is_data_changed)
    print("---Antwort---\n", response)

    return (response, state_running_task, tagged_tokens)


# COMMAND PROMPT EXEC
if __name__ == "__main__":

    state_running_task = tagged_tokens = {}

    opening_messsage = 'Okay, lass uns per Terminal chatten!\n' + \
        '[Eingabe "task": Stand des aktuell bearbeiteten Tasks ausgeben]\n' + \
        '[Eingabe "tokens": Ermittelte Tokens der letzten Nachricht ausgeben]\n' + \
        '[Eingabe "data": Studierendendaten ausgeben]\n' + \
        '[Eingabe "exit": Chat beenden]'
    print(opening_messsage)

    while True:
        message = input().strip()

        if (not message):
            continue

        elif message.lower() == "task":
            print(json.dumps(state_running_task, indent=4))

        elif message.lower() == "tokens":
            print(json.dumps(tagged_tokens, indent=4))
            continue

        elif message.lower() == "data":
            print(json.dumps(students, indent=4))
            continue

        elif message.lower() == "exit":
            print('Danke! Bis bald!')
            break

        response, state_running_task, tagged_tokens = get_response(
            message, state_running_task, tagged_tokens
        )

        # break
