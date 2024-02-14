from spylls.hunspell import Dictionary

spylls_dictionary = Dictionary.from_files(
    "./preprocessing/additional_dictionaries/de_DE"
)


def autocorrect_word(word):
    # Prüfen, ob Wort bekannt/im Wörterbuch vorhanden, wenn nicht, ersten Vorschlag zurückgeben
    if (spylls_dictionary.lookup(word) == False):
        for suggestion in spylls_dictionary.suggest(word):
            return suggestion if suggestion else word
    return word
