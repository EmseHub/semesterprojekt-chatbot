import re
import string
# import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag, RegexpParser
from HanTa import HanoverTagger as hanta

# from .spelling_correction import autocorrect_tokens

hanover_tagger = hanta.HanoverTagger("morphmodel_ger.pgz")


def get_tagged_tokens_with_ner(raw_text):
    print("------- NER -------")
    from nltk.chunk import tree2conlltags

    # ---Englisch---
    clean_text = "The little yellow dog barked at the cat. Thomas likes Hollywood a lot."
    tokens = word_tokenize(clean_text, "english")
    tagged_tokens = pos_tag(tokens)
    print("---tagged_tokens ENG---\n", tagged_tokens)
    # Noun Phrase Chunking:
    # Our chunk pattern consists of one rule, that a noun phrase (NP) should be formed whenever the chunker
    # finds an optional determiner (DT), followed by any number of adjectives (JJ), and then a noun (NN)
    # https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da
    grammar = "NP: {<DT>?<JJ>*<NN>}"
    cp = RegexpParser(grammar)
    result = cp.parse(tagged_tokens)
    print("---result ENG---\n", result)
    iob_tagged = tree2conlltags(result)
    print("---iob_tagged ENG---\n", iob_tagged)

    # ---Deutsch---
    clean_text = "Der kleine gelbe Hund hat die Katze angebellt."
    tokens = word_tokenize(clean_text, "german")
    tagged_tokens = hanover_tagger.tag_sent(tokens)
    tagged_tokens = [
        (tagged_token[0], tagged_token[2]) for tagged_token in tagged_tokens
    ]
    print("---tagged_tokens GER---\n", tagged_tokens)
    grammar = "NP: {<ART>?<ADJ\\(A\\)>*<NN>}"
    cp = RegexpParser(grammar)
    result = cp.parse(tagged_tokens)
    print("---result GER---\n", result)
    iob_tagged = tree2conlltags(result)
    print("---iob_tagged GER---\n", iob_tagged)
    # Weitere Schritte erforderlich...

    return (None, None)

    # Mögliche Ansätze
    # Flair -> https://huggingface.co/flair/ner-german-large
    # BERT -> https://jupiter.fh-swf.de/projects/ner/ und https://huggingface.co/fhswf/bert_de_ner
    # Electra?


# print(get_tagged_tokens_with_ner(""))


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

    # Tokens, die eine Mindestanzahl an Zeichen unterschreite entfernen
    filtered_tokens_word = [
        token for token in filtered_tokens_word if len(token) > 1
    ]

    # Parts-of-Speech-Tagging

    # ---NLTK---
    # Nur Englisch und Russisch
    # tagged_tokens = pos_tag(filtered_tokens_word)

    # ---Hanover Tagger---
    # Deutsch, Niederländisch und Englisch
    # https://github.com/wartaal/HanTa
    # https://github.com/wartaal/HanTa/blob/master/Demo.ipynb
    # https://textmining.wp.hs-hannover.de/Preprocessing.html#Lemmatisierung-und-Wortarterkennung
    # POS-Tags auflisten:
    #   hanover_tagger.list_postags()
    #   hanover_tagger.list_mtags()
    # HanTa-Tags entsprechen dem Stuttgart-Tübingen-Tagset (STTS)
    # https://www.ims.uni-stuttgart.de/forschung/ressourcen/lexika/germantagsets/#id-cfcbf0a7-0
    # https://homepage.ruhr-uni-bochum.de/stephen.berman/Korpuslinguistik/Tagsets-STTS.html
    # https://www.ims.uni-stuttgart.de/documents/ressourcen/korpora/tiger-corpus/annotation/tiger_scheme-morph.pdf (pp 26/27)

    # print(hanover_tagger.analyze("Zauberkunde"))
    # print(hanover_tagger.analyze("Dortmund"))
    # print(hanover_tagger.analyze("Meyer"))
    # print(hanover_tagger.analyze("Stein"))

    taglevel = 1  # Default ist 1
    casesensitive = False  # Default ist True
    tagged_tokens = hanover_tagger.tag_sent(
        filtered_tokens_word, taglevel, casesensitive
    )

    # ---Weitere Optionen---
    # "Pattern" Library des CLiPS Research Center
    # https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/

    # Stop Words erneut entfernen, anhand lemmata?

    # Named-Entity-Recognition (Personen, Orte und Organisationen) --> In Regelsystem ausgelagert, damit bei unvollständigen Entitäten direkt Rückfragen gestellt werden können
    # Benötigte Entitäten: Personen, Mat.-Nr, ...

    return ([tagged_token[0] for tagged_token in tagged_tokens], diagnostic)
    # print(" ".join(filtered_tokens_word))
