#  Möglicher Einstieg
#  https://stackoverflow.com/questions/13928155/spell-checker-for-python
#  https://norvig.com/spell-correct.html

#  https://medium.com/@yashj302/spell-check-and-correction-nlp-python-f6a000e3709d

#   JAMSPELL *********************************************************************
#   ******************************************************************************

#   -> Jamspell     pipenv install jamspell
    
#    https://github.com/bakwc/JamSpell
#    In C++ geschrieben, braucht daher swig3, idealerweise einen anderen Spellchecker einsetzen... 
#      Supported Languages?
#      https://wortschatz.uni-leipzig.de/en/download/German


#   TEXTBLOB *********************************************************************
#   ******************************************************************************
#   -> Textblob     pipenv install textblob (-> P. Norvig)
#                    pipenv install textblob-de

#       https://www.geeksforgeeks.org/spelling-checker-in-python/

#       https://textblob-de.readthedocs.io/en/latest/
#       -> textblob-de = German Language Extension for TextBlob (Standard = Englisch)

#       -> Correct-Function für Deutsch nicht verfügbar...


#   PYSPELLCHECKER ***************************************************************
#   ******************************************************************************
#       pipenv install pyspellchecker

#       https://github.com/sagorbrur/bengali_pyspellchecker

from spellchecker import SpellChecker

def autocorrect_word(word):

    spell = SpellChecker(language='de')

    corrected_word = spell.correction(word)
    #print(corrected_word)

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
sample_tokens = ["Dase", "its", "einne", "Beispil-Nachriecht", "Aber", "mit","Fehlren", "von" ,"Dr.", "House"]
#sample_tokens = ["Thsi", "comptuer", "extnsions"]

print(autocorrect_tokens(sample_tokens))