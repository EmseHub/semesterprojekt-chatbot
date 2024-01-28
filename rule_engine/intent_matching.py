from helpers.helpers import parse_json_file

parsed_intents = parse_json_file('rule_engine/intents.json')


def replace_diacritics(text):
    # TO DO...
    # Umlaute etc. aufbrechen
    return text


def get_intent_NEW(tagged_tokens):
    # TO DO...
    intent = {}
    return intent

# auch "intent recognition"
# https://botfriends.de/en/blog/botwiki/intents/
# https://www.geeksforgeeks.org/intent-recognition-using-tensorflow/


def get_intent(tagged_tokens):
    # Übernommen aus JS-Demo
    if not tagged_tokens or len(tagged_tokens) == 0:
        return None
    tagged_tokens_no_diacritics = [
        replace_diacritics(tagged_token.lower()) for tagged_token in tagged_tokens
    ]
    total_words = len(tagged_tokens_no_diacritics)
    possible_intents = []
    for obj_intent in parsed_intents:
        hit_count = 0
        for str_pattern in obj_intent['patterns']:
            if str_pattern in tagged_tokens_no_diacritics:
                hit_count += 1
        if hit_count < obj_intent['min_hits']:
            continue
        if hit_count >= total_words:
            return {**obj_intent, 'hit_count': hit_count}
        if hit_count > 0:
            possible_intents.append({**obj_intent, 'hit_count': hit_count})
    if len(possible_intents) == 0:
        return {**next(intent for intent in parsed_intents if intent['tag'] == 'trefferlos'), 'hit_count': 0}
    print('Mögliche Intents', possible_intents)
    return max(possible_intents, key=lambda intent: intent['hit_count'])
