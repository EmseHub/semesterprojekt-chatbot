import re
import string
# import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag


def get_tokenized_text(raw_text):
    language = "german"

    # Mehrfache Leerzeichen, Tabs und Zeilenumbrüche mit RegEx auf ein Leerzeichen reduzieren
    clean_text = re.sub("\\s+", " ", raw_text)

    # Tokenization
    tokens_sentence = sent_tokenize(clean_text, language)
    tokens_word = word_tokenize(clean_text, language)

    # Stop-Words entfernen (case-insensitive besser?)
    filtered_tokens_word = [
        token for token in tokens_word if token not in stopwords.words(language)
    ]

    # Satzzeichen entfernen
    filtered_tokens_word = [
        token for token in filtered_tokens_word if token not in string.punctuation
    ]

    # Tokens, die eine Mindestanzahl an Zeichen unterschreite entfernen
    filtered_tokens_word = [
        token for token in filtered_tokens_word if len(token) > 1]

    # Parts-of-Speech-Tagging
    tagged_tokens = pos_tag(filtered_tokens_word)

    print(tokens_sentence)
    print('---------------')
    print(tokens_word)
    print('---------------')
    print(filtered_tokens_word)
    print('---------------')
    print(tagged_tokens)
    print('---------------')
    response = " ".join(filtered_tokens_word)
    print(response)

    return response


# https://fortext.net/routinen/lerneinheiten/preprocessing-mit-nltk
