from operator import itemgetter

from preprocessing.preprocessing import get_tagged_tokens
from rule_engine.intent_matching import get_intent
from rule_engine.tasks import process_task

# Globale Variable über den aktuell bearbeiteten Task
state_running_task = {}


def get_response(message):

    global state_running_task

    tagged_tokens = get_tagged_tokens(message)

    intent = get_intent(tagged_tokens)

    state_running_task, response, is_data_changed = itemgetter("state_running_task", "response", "is_data_changed")(
        process_task(state_running_task, tagged_tokens, message, intent)
    )

    diagnostic = {
        "tagged_tokens": tagged_tokens,
        "intent": intent,
        "state_running_task": state_running_task,
        "is_data_changed": is_data_changed
    }

    return (response, diagnostic)
