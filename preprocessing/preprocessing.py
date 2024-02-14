import re
import string

from nltk.tokenize import word_tokenize
from HanTa import HanoverTagger as hanta

from data.data_service import students, courses
from preprocessing.spelling_correction import autocorrect_word

# HanoverTagger mit Modell initialisieren
hanover_tagger = hanta.HanoverTagger("morphmodel_ger.pgz")

# Bekannte Begriffe, die aus Performanzgründen von der Rechtschreibkorrektur ausgenommen werden sollen
words_not_to_correct = ["Muggel"]
for student in students:
    words_not_to_correct += student["vorname"].split()
    words_not_to_correct += student["nachname"].split()
    words_not_to_correct += student["adresse"]["strasse"].split()
    words_not_to_correct += student["adresse"]["stadt"].split()
for course in courses:
    words_not_to_correct += course["name"].split()

# Maximal zulässige Wortlänge, ab deren Überschreitung Begriffe aus Performanzgründen von der Rechtschreibkorrektur ausgenommen werden
max_wordlength_to_correct = 15


def get_tagged_tokens(text_raw):

    language = "german"

    # Mehrfache Leerzeichen, Tabs und Zeilenumbrüche mit RegEx auf ein Leerzeichen reduzieren
    clean_text = re.sub(r"\s+", " ", text_raw)

    # Tokenization auf Wort-Ebene
    tokens_original = word_tokenize(clean_text, language)

    # Satzzeichen entfernen
    tokens_original = [
        token for token in tokens_original if token not in string.punctuation
    ]

    # Tokens, die eine Mindestanzahl an Zeichen unterschreiten, entfernen [aktuell genügt ein Zeichen]
    tokens_original = [
        token for token in tokens_original if len(token) > 0
    ]

    # Rechtschreibkorrektur
    tokens_corrected = [
        token if (
            (re.search(r"[^A-ZÄÖÜa-zäöüß]", token))
            or (token in words_not_to_correct)
            or (len(token) > max_wordlength_to_correct)
        ) else autocorrect_word(token) for token in tokens_original
    ]

    # Part-of-Speech-Tagging und Lemmatisierung

    # ---Hanover Tagger---
    # Deutsch, Niederländisch und Englisch
    # https://github.com/wartaal/HanTa
    # https://github.com/wartaal/HanTa/blob/master/Demo.ipynb --> Doku
    # https://textmining.wp.hs-hannover.de/Preprocessing.html#Lemmatisierung-und-Wortarterkennung
    # POS-Tags auflisten:
    #   hanover_tagger.list_postags()
    #   hanover_tagger.list_mtags()
    # HanTa-Tags entsprechen dem Stuttgart-Tübingen-Tagset (STTS)
    # https://www.ims.uni-stuttgart.de/forschung/ressourcen/lexika/germantagsets/#id-cfcbf0a7-0
    # https://homepage.ruhr-uni-bochum.de/stephen.berman/Korpuslinguistik/Tagsets-STTS.html
    # https://www.ims.uni-stuttgart.de/documents/ressourcen/korpora/tiger-corpus/annotation/tiger_scheme-morph.pdf (S. 26/27)

    taglevel = 1  # Default ist 1
    casesensitive = True  # Default ist True
    tokens_hannover_tagged = hanover_tagger.tag_sent(
        tokens_corrected, taglevel, casesensitive
    )

    # ---Weitere Optionen---
    # "Pattern" Library des CLiPS Research Center
    # https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/

    # Tags je Token zusammenführen und als Liste ausgeben
    result_tagged_tokens = [
        {
            "original": tokens_original[i],
            "korrigiert": tokens_corrected[i],
            "lemma": tokens_hannover_tagged[i][1],
            "pos": tokens_hannover_tagged[i][2]
        }
        for i in range(len(tokens_original))
    ]

    return result_tagged_tokens
