from preprocessing import nltk_pipeline
from rule_engine import intent_matching, rules, entity_detection

state_running_task = {}


def get_response(message):
    # Temp-Test:
    return ""

    (tagged_tokens, diagnostic) = nltk_pipeline.get_tagged_tokens(message)
    print("---Tagged Tokens---\n", tagged_tokens)
    print("---Diagnostic---\n", diagnostic)

    intent = intent_matching.get_intent(tagged_tokens)
    print("---Gefundener Intent---\n", intent)

    (new_state_running_task, response, is_data_changed) = rules.process_task(
        state_running_task, tagged_tokens, intent
    )
    # TODO: state_running_task müsste hier noch mit dem neuen Wert überschrieben werden, damit ein ggf. neuer oder weiterhin
    # bestehender Task in der neuen Iteration wieder an die Funktion process_task übergeben und dann weiter bearbeitet wird (?).
    print("---Running-Task---\n", new_state_running_task)
    print("---Rückfrage---\n", response)
    print("---Daten verändert?---\n", is_data_changed)

    # print(tagged_tokens)
    # print(diagnostic)
    # print(new_state_running_task)
    # print(query)

    # response ("query") ausgeben
    return response


# COMMAND PROMPT EXEC
if __name__ == "__main__":
    # print("Okay, lass uns per Terminal chatten! (type 'exit' to cancel)")
    while True:
        # message = input()
        # if message.lower() == "exit":
        #     break

        # response = get_response(message.strip())
        # print(response)

        sample_message = "Das ist eine Beispiel-Nachricht, Aber mit Fehlren und  Leerzeichen. Sie wurde z.B. verfasst von Dr. House und Mr. X, während der Hg. Homer ist."
        response = get_response(sample_message.strip())
        print(response)
        break
