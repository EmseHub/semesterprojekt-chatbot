import re
import string
# import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from HanTa import HanoverTagger as hanta

from .spelling_correction import autocorrect_tokens


def get_tagged_tokens(raw_text):

    diagnostic = {}
    language = "german"

    # Mehrfache Leerzeichen, Tabs und Zeilenumbrüche mit RegEx auf ein Leerzeichen reduzieren
    clean_text = re.sub("\\s+", " ", raw_text)

    # Tokenization
    tokens_sentence = sent_tokenize(clean_text, language)
    tokens_word = word_tokenize(clean_text, language)

    # Satzzeichen entfernen
    filtered_tokens_word = [
        token for token in tokens_word if token not in string.punctuation
    ]

    # # Stop-Words entfernen (case-insensitive besser?)
    # filtered_tokens_word = [
    #     token for token in filtered_tokens_word if token not in stopwords.words(language)
    # ]

    # # Tokens, die eine Mindestanzahl an Zeichen unterschreite entfernen
    # filtered_tokens_word = [
    #     token for token in filtered_tokens_word if len(token) > 1
    # ]

    # Parts-of-Speech-Tagging
    tagged_tokens = pos_tag(filtered_tokens_word)

    # ---- TEST ----
    # Hanover Tagger
    # https://github.com/wartaal/HanTa
    # https://github.com/wartaal/HanTa
    # https://github.com/wartaal/HanTa/blob/master/Demo.ipynb
    # https://textmining.wp.hs-hannover.de/Preprocessing.html#Lemmatisierung-und-Wortarterkennung

    hanover_tagger = hanta.HanoverTagger('morphmodel_ger.pgz')
    # print(hanover_tagger.analyze('Fachmärkte'))
    tagged_tokens = hanover_tagger.tag_sent(filtered_tokens_word)

    # Pattern library rom CLiPS Research Center
    # https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/

    print('------- tokens_sentence -------')
    print(tokens_sentence)
    print('------- tokens_word -------')
    print(tokens_word)
    print('------- filtered_tokens_word -------')
    print(filtered_tokens_word)
    print('------- tagged_tokens -------')
    print(tagged_tokens)

    # print('---------------')
    # print(" ".join(filtered_tokens_word))

    return (tagged_tokens, diagnostic)


# https://fortext.net/routinen/lerneinheiten/preprocessing-mit-nltk
