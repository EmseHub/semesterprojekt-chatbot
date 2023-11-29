# Hierhin können Hilfsfunktionen ausgelagert werden
from time import sleep, time
from src.constants import TASKS, DEBUG, LOADING_ANIMATION_SET
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download module resources (initially needed)
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')


# Beispiel
def doStuff():
    """
    This is an example for a description of what the function does.
    """
    print("Doing Stuff")


# CHAT OUTPUT Helpers
def studentInput(text=""):
    inp = input("Student: " + text)
    return inp


def chatbotAnswer(text=""):
    print("Chatbot: " + text + "\n")


def printAvailableFunctions():
    print("Das sind die Aufgaben, die ich für dich übernehmen kann:\n")
    for task in TASKS:
        print("- ", task)


# Chat Loading Animations
def loadingAnimation(duration=1, variant=1):
    animation_set = LOADING_ANIMATION_SET
    # create valid variant numbers
    valid = len(animation_set)
    # default to nr.1 if chosen variant nr is not existent
    if variant > valid:
        variant = 1

    # set chosen animation, index starts with 0
    animation = animation_set[variant - 1]

    # set duration timeout (passed time + duration)
    timeout = time() + duration

    index = 0
    while True:
        print(animation[index % len(animation)], end="\r")
        index += 1
        sleep(0.2)
        if time() > timeout:
            print(" " * 100, flush=True)
            sleep(0.1)
            break


def loadingAnimation2(dots=3, seconds=0.8):
    """
    Wait, let the bot pretend thinking about an answer (mimic human response).
    """
    for i in range(dots):
        sleep(seconds)
        print(".", end=" ", flush=True)
    sleep(seconds)
    print("\n")


# NLP PIPELINE


def getResponse(text: str):
    """
    Takes a text to do all the NLP processing on it to get the intent. Returns the response message.
    """
    # TODO preprocessing pipeline:

    # tokenize
    # remove stopwords
    # pos_tagging
    # stemming/lemmatization
    # bag of words
    # get intent by similiarity of intents.data?
    # choose random response of the intent tag
    # return text

    response = "Hm... das weiß ich leider auch nicht."
    return response


def getSentences(text: str):
    sentences = nltk.sent_tokenize(text)
    return sentences


def getTokens(text: str):
    tokens = nltk.word_tokenize(text)
    return tokens


def doSpellcheck(text: list[str]):
    # TODO
    return


def removeStopwords(tokens: list[str]):
    stop_words = stopwords.words("german")

    # filter out stopwords
    filtered_tokens = [w for w in tokens if not w in stop_words]

    return filtered_tokens


def doPosTagging(tokens: list[str]):
    # TODO
    return


def doLemmatization(tokens: list[str]):
    # TODO WordNetLemmatizer only for english? Use spaCy for german words!
    # lowercase tokens for lemmatizer
    tokens = [t.lower() for t in tokens]

    lemmatizer = WordNetLemmatizer()
    result = [lemmatizer.lemmatize(token) for token in tokens]
    return result


def doStemming(tokens: list[str]):
    # TODO (not needed if lemmatization is used)
    return


def getIntent(text):
    print(DEBUG, "Trying to get the intent...")
    # check the intent


# test ouput
def test():
    text = "Ich ging vorhin in den Wald. Dort sah ich Peter, der gerade am Joggen war."
    tokens = getTokens(text)
    print(DEBUG, "TOKENS", tokens)

    filtered_text = removeStopwords(tokens)
    print(DEBUG, "FILTER", filtered_text)

    lemmatized_text = doLemmatization(filtered_text)
    print(DEBUG, "LEMMA", lemmatized_text)
