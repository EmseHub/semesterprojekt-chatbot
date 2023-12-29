from preprocessing import nltk_pipeline
from rule_engine import intent_matching, rules

state_running_task = {}


def get_response(message):
    (tagged_tokens, diagnostic) = nltk_pipeline.get_tagged_tokens(message)
    intent = intent_matching.get_intent(tagged_tokens)

    print("---Gefundener Intent---\n", intent)

    (new_state_running_task, query) = rules.process_task(
        tagged_tokens, intent, state_running_task
    )

    print("---Running-Task---\n", new_state_running_task)
    print("---Rückfrage---\n", query)

    # print(tagged_tokens)
    # print(diagnostic)
    # print(new_state_running_task)
    # print(query)
    return "TO DO"


# Input via Terminal (später ersetzt durch String vom Frontend)
while True:
    # message = input()
    # print("Eingabe:\n" + message)
    # if message.lower() == "exit":
    #     break

    sample_message = "Das ist eine Beispiel-Nachricht, Aber mit Fehlren und  Leerzeichen. Sie wurde z.B. verfasst von Dr. House und Mr. X, während der Hg. Homer ist."
    response = get_response(sample_message.strip())
    # print(response)
    break
