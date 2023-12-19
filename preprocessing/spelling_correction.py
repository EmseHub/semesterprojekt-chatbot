#  Möglicher Einstieg
#  https://stackoverflow.com/questions/13928155/spell-checker-for-python
#  https://norvig.com/spell-correct.html

#  https://medium.com/@yashj302/spell-check-and-correction-nlp-python-f6a000e3709d
#   -> Jamspell     pip install jamspell
#   -> Symspellpy   pip install symspellpy
#   -> Textblob     pip install textblob (-> P. Norvig)

def autocorrect_word(word):
    corrected_word = "TO DO" + word
    return corrected_word


def autocorrect_tokens(tokens):
    if not tokens:
        # Liste ist leer...
        return []
    
    corrected_tokens = []
    for token in tokens:
        corrected_token = autocorrect_word(token)
        corrected_tokens.append(corrected_token)

    return corrected_tokens


# Beispiel-Liste zum Testen
# sample_tokens = ["Das", "its", "einne" "Beispil-Nachriecht", "Aber", "mit","Fehlren", "von" ,"Dr.", "House"]
# print(autocorrect_tokens(sample_tokens))