import re
import string
# import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag, RegexpParser
from HanTa import HanoverTagger as hanta

from .spelling_correction import autocorrect_word
# from spelling_correction import autocorrect_word

words_not_to_process = ['Muggel']
hanover_tagger = hanta.HanoverTagger("morphmodel_ger.pgz")


def get_tagged_tokens_with_ner(text_raw):
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


def get_tagged_tokens(text_raw):

    language = "german"

    # Mehrfache Leerzeichen, Tabs und Zeilenumbrüche mit RegEx auf ein Leerzeichen reduzieren
    clean_text = re.sub(r"\s+", " ", text_raw)

    # Tokenization auf Wort-Ebene
    tokens_original = word_tokenize(clean_text, language)
    # tokens_sentence = sent_tokenize(clean_text, language)

    # Satzzeichen entfernen
    tokens_original = [
        token for token in tokens_original if token not in string.punctuation
    ]

    # Tokens, die eine Mindestanzahl an Zeichen unterschreiten, entfernen
    tokens_original = [
        token for token in tokens_original if len(token) > 0
    ]

    # Stop-Words entfernen (case-insensitive besser?) --> Stop-Words nach HanTa erneut entfernen, anhand lemmata/Korrektur?
    # tokens_original = [
    #     token for token in tokens_original if token not in stopwords.words(language)
    # ]

    # Rechtschreibkorrektur
    tokens_corrected = [
        token if ("." in token or token in words_not_to_process) else autocorrect_word(token) for token in tokens_original
    ]

    # Parts-of-Speech-Tagging

    # ---NLTK---
    # Nur Englisch und Russisch
    # tagged_tokens = pos_tag(tokens_original)

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

    taglevel = 1  # Default ist 1
    casesensitive = False  # Default ist True
    tokens_hannover_tagged = hanover_tagger.tag_sent(
        tokens_corrected, taglevel, casesensitive
    )
    # tokens_hannover_tagged = [ hanover_tagger.analyze(token) for token in tokens_corrected ]
    # print(hanover_tagger.analyze("wurde")) --> Ausgabe zu "wurde" ist ('wurde', 'werden', 'VA(FIN)'

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


# sample_message = "mein ist Muggel sauer"
# sample_message = "Das ist eine Beispiel-Nachricht, Aber mit Fehlren und  Leerzeichen. Sie wurde z.B. verfasst von Dr. House und Mr. X, während der Hg. Homer ist."
# print('---get_tagged_tokens(sample_message)----')
# print(get_tagged_tokens(sample_message))
