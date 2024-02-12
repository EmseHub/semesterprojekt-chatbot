from operator import itemgetter

from preprocessing.preprocessing import get_tagged_tokens
from rule_engine.intent_matching import get_intent
from rule_engine.tasks import process_task

from rule_engine.data_service import students, courses


state_running_task = {}


def get_response(message):

    global state_running_task

    tagged_tokens = get_tagged_tokens(message)

    intent = get_intent(tagged_tokens)
    # print("---Gefundener Intent---\n", intent.get("tag"))

    state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
        process_task(state_running_task, tagged_tokens, message, intent)
    )
    # print("---Daten verändert---\n", is_data_changed)

    diagnostic = {
        "tagged_tokens": tagged_tokens.copy(),
        "intent": intent.copy(),
        "state_running_task": state_running_task
    }
    # print("---Diagnostic---\n", diagnostic)

    return (response, diagnostic, is_data_changed, students, courses)
