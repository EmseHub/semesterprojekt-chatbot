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

    # --NLTK--
    # tagged_tokens = pos_tag(filtered_tokens_word)

    # --Hanover Tagger--
    # https://github.com/wartaal/HanTa
    # https://github.com/wartaal/HanTa/blob/master/Demo.ipynb
    # https://textmining.wp.hs-hannover.de/Preprocessing.html#Lemmatisierung-und-Wortarterkennung

    hanover_tagger = hanta.HanoverTagger('morphmodel_ger.pgz')

    # POS-Tags auflisten
    # hanover_tagger.list_postags()
    # hanover_tagger.list_mtags()

    # HanTa-Tags entsprichen dem Stuttgart-Tübingen-Tagset (STTS)
    # https://www.ims.uni-stuttgart.de/forschung/ressourcen/lexika/germantagsets/#id-cfcbf0a7-0
    # https://homepage.ruhr-uni-bochum.de/stephen.berman/Korpuslinguistik/Tagsets-STTS.html
    # https://www.ims.uni-stuttgart.de/documents/ressourcen/korpora/tiger-corpus/annotation/tiger_scheme-morph.pdf (pp 26/27)

    # print(hanover_tagger.analyze('Fachmärkte'))

    taglevel = 1
    casesensitive = False
    tagged_tokens = hanover_tagger.tag_sent(
        filtered_tokens_word, taglevel, casesensitive
    )

    # Pattern library rom CLiPS Research Center
    # https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/

    # Stop Words erneut entfernen, anhand lemmata?

    # Named-Entity-Recognition

    # Ideen
    # Flair -> https://huggingface.co/flair/ner-german-large
    # BERT -> https://jupiter.fh-swf.de/projects/ner/ und https://huggingface.co/fhswf/bert_de_ner
    # Electra?

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
