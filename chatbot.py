import json
from operator import itemgetter

from preprocessing import nltk_pipeline
from rule_engine import intent_matching, rules

from rule_engine.data_service import students


state_running_task = tagged_tokens = {}


def get_response(message):

    global state_running_task, tagged_tokens

    # Temp-Test:
    # return ""

    # print(message)

    tagged_tokens = nltk_pipeline.get_tagged_tokens(message)
    # print("---Tagged Tokens---\n", tagged_tokens)

    # diagnostic = tagged_tokens.copy()
    # print("---Diagnostic---\n", diagnostic)

    intent = intent_matching.get_intent(tagged_tokens)
    print("---Gefundener Intent---\n", intent.get("tag"))
    # print('[Gefundener Intent: "' + intent.get("tag") + '"]')

    state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
        rules.process_task(state_running_task, tagged_tokens, message, intent)
    )

    # print("---Running-Task---\n", state_running_task)
    print("---Daten verändert---\n", is_data_changed)
    # print("[Daten verändert: " + str(is_data_changed) + "]")
    print("---Antwort---\n", response)
    # print("[Rückfrage : " + response + "]")

    return response


# COMMAND PROMPT EXEC
if __name__ == "__main__":

    # state_running_task = tagged_tokens = {}

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

        # response = get_response(message.strip())
        # print(response)

        sample_message = "Das ist eine Beispiel-Nachricht, Aber mit Fehlren und  Leerzeichen. Sie wurde z.B. verfasst von Dr. House und Mr. X, während der Hg. Homer ist."
        sample_message = "Ich würde gerne meine Adresse ändern, meine Matrikelnummer ist 1234567 und meine neue Adresse lautet Am Hang 55a in 50737 Köln"
        sample_message = "Ich würde gerne meine Adresse ändern, meine Matrikelnummer ist 1234567 und meine neue Hausnummer ist 55a in 50737 Köln"

        response = get_response(message)
        # print(response)
        # break
