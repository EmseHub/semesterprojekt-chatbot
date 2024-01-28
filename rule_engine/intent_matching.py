from rule_engine.helpers import parse_json_file

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

    # Umlaute ersetzen und Tokens in Lower Case umwandeln (man weiß nie, wie User Texte eingibt)
    tagged_tokens_no_diacritics = [
        replace_diacritics(tagged_token.lower()) for tagged_token in tagged_tokens
    ]

    total_words = len(tagged_tokens_no_diacritics)
    possible_intents = []

    for intent in parsed_intents:
        # Anzhahl der Patterns des Intents, die von der Nachricht getroffen werden
        hit_count = 0
        for pattern in intent['patterns']:
            if pattern in tagged_tokens_no_diacritics:
                # Pattern getroffen
                hit_count += 1
        if hit_count < intent['min_hits']:
            # Im Intent definiertes Minimum an Treffern nicht erreicht
            continue
        if hit_count >= total_words:
            # Jedes Wort der Nachricht trifft -> Intent eindeutig
            return {**intent, 'hit_count': hit_count}
        if hit_count > 0:
            # Möglicherweise gemeinten Intent zur Liste hinzufügen
            possible_intents.append({**intent, 'hit_count': hit_count})

    if len(possible_intents) == 0:
        # Kein Treffer -> Default-Intent ausgeben
        return {**next(intent for intent in parsed_intents if intent['tag'] == 'trefferlos'), 'hit_count': 0}

    # Intent mit den meisten Treffern ausgeben
    print('Mögliche Intents', possible_intents)
    return max(possible_intents, key=lambda intent: intent['hit_count'])
