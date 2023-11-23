# Hierhin können Hilfsfunktionen ausgelagert werden
from time import sleep, time
from src.constants import TASKS, DEBUG, LOADING_ANIMATION_SET
import nltk


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


# (test)
def loadingAnimation2(dots=3, seconds=0.8):
    """
    Wait, let the bot pretend thinking about an answer (mimic human response).
    """
    for i in range(dots):
        sleep(seconds)
        print(".", end=" ", flush=True)
    sleep(seconds)
    print("\n")


# NLP PIPELINE Helpers
def getSentences(text):
    sentences = nltk.sent_tokenize(text)
    return sentences


def getTokens(text):
    tokens = nltk.tokenize(text)
    return tokens


def doLemmatization(tokens):
    lemmatizer = nltk.WordNetLemmatizer
    result = [lemmatizer.lemmatize(token) for token in tokens]
    return result


def getIntent(text):
    print(DEBUG, "Trying to get the intent...")
    # check the intent
