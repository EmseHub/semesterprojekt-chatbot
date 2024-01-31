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

# from spellchecker import SpellChecker
# spell = SpellChecker(language='de')

# corrected_word = spell.correction(word)
# print(corrected_word)
# print(spell.candidates(word))

# Falsche/fehlerhaftes Wort identifizieren
# corrected_word = spell.correction(word)

# if corrected_word != None:
#   print("Korrektur: " + corrected_word)
# else:
#    print("Kein Fehler: " + word)


#   HUNSPELL *********************************************************************
#   ******************************************************************************
#       pipenv install phunspell

#       https://github.com/pyhunspell/pyhunspell
#       https://datascience.blog.wzb.eu/2016/07/13/autocorrecting-misspelled-words-in-python-using-hunspell/
#       https://pypi.org/project/phunspell/

#   print(pspell.lookup("phunspell")) # False
#   print(pspell.lookup("about")) # True

#   mispelled = pspell.lookup_list("Bill's TV is borken".split(" "))
#   print(mispelled) # ["borken"]

#    for suggestion in pspell.suggest('phunspell'):
#        print(suggestion) # Hunspell

import phunspell
pspell = phunspell.Phunspell('de_DE')


def autocorrect_word(word):
    # Prüft, ob Wort bekannt/im Wörterbuch vorhanden (true/false)
    if pspell.lookup(word) == False:
        for suggestion in pspell.suggest(word):
            return suggestion if suggestion else word
    return word


# Beispiel-Liste zum Testen
# sample_tokens = ["Dase", "its", "einne", "Beispil-Nachriecht", "Aber", "mit", "Fehlren", "von", "Dr.", "House"]
# sample_tokens = ["meina", "its", "Muggel",  "saure"]
# print([autocorrect_word(token) for token in sample_tokens])
