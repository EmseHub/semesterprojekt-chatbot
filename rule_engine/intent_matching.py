from rule_engine.helpers import parse_json_file, replace_diacritics

parsed_intents = parse_json_file('rule_engine/intents.json')

# auch "intent recognition"
# https://botfriends.de/en/blog/botwiki/intents/
# https://www.geeksforgeeks.org/intent-recognition-using-tensorflow/


def get_intent(tagged_tokens):

    if (not tagged_tokens or len(tagged_tokens) == 0):
        return None

    # Anzahl der Wörter im Text
    total_words = len(tagged_tokens)

    possible_intents = []
    for intent in parsed_intents:
        # Anzhahl der Patterns des Intents, die vom Text getroffen werden
        hit_count = 0

        for pattern in intent['patterns']:
            # Prüfen, ob Pattern des Intents zu Lemma oder Original-Wort des Textes passt
            for tagged_token in tagged_tokens:
                # Original-Wort und Lemma extrahieren und zum Abgleich ins Format der Patterns umwandeln: Umlaute ersetzen und Lower Case
                original = replace_diacritics(tagged_token["original"].lower())
                lemma = replace_diacritics(tagged_token["lemma"].lower())
                if (pattern == original or pattern == lemma):
                    # Pattern getroffen
                    hit_count += 1
                    # Nur ein Treffer je Token möglich
                    continue

        if hit_count < intent['min_hits']:
            # Im Intent definiertes Minimum an Treffern nicht erreicht
            continue
        if hit_count >= total_words:
            # Jedes Wort des Textes trifft -> Intent eindeutig
            return {**intent, 'hit_count': hit_count}
        if hit_count > 0:
            # Möglicherweise gemeinten Intent zur Liste hinzufügen
            possible_intents.append({**intent, 'hit_count': hit_count})

    # Falls kein Intent gefunden wurde, Default-Intent ausgeben
    if len(possible_intents) == 0:
        return {**next(intent for intent in parsed_intents if intent['tag'] == 'trefferlos'), 'hit_count': 0}

    # Intent mit den meisten Treffern ausgeben
    # print('Mögliche Intents', possible_intents)
    return max(possible_intents, key=lambda intent: intent['hit_count'])
