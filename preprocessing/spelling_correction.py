#  Möglicher Einstieg
#  https://stackoverflow.com/questions/13928155/spell-checker-for-python
#  https://norvig.com/spell-correct.html

#  https://medium.com/@yashj302/spell-check-and-correction-nlp-python-f6a000e3709d

#   JAMSPELL *********************************************************************
#   ******************************************************************************

#   -> Jamspell     pipenv install jamspell
#      Supported Languages?
#      https://wortschatz.uni-leipzig.de/en/download/German

#       import jamspell

#       corrector = jamspell.TSpellCorrector()
#       corrector.LoadLangModel('en.bin')

#       corrector.FixFragment('I am the begt spell cherken!')
#       u'I am the best spell checker!'

#       corrector.GetCandidates(['i', 'am', 'the', 'begt', 'spell', 'cherken'], 3)
#       (u'best', u'beat', u'belt', u'bet', u'bent', ... )

#       corrector.GetCandidates(['i', 'am', 'the', 'begt', 'spell', 'cherken'], 5)
#       (u'checker', u'chicken', u'checked', u'wherein', u'coherent', ...)



#   -> Symspellpy   pipenv install symspellpy
#   -> Textblob     pipenv install textblob (-> P. Norvig)

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