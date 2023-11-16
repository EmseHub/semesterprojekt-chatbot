"PYTHON CHATBOT Semesterprojekt"
# setup: import outsourced files/functions
from src.constants import *
from src.helpers import *

# import third-party modules
from time import sleep
import nltk

# nltk.download('punkt')

# start chat loop with welcome message
print(WELCOME)
printAvailableFunctions()
print(DIVIDER)

while True:
    # read users input
    text = studentInput()

    # check if user wants to exit or needs help
    if str(text).lower() in EXIT_MESSAGES:
        break
    if str(text).lower() in ["help", "hilfe"]:
        printAvailableFunctions()
        continue

    # NLP PIPELINE
    # tokenize the users input text
    # sentences = nltk.sent_tokenize(text)
    # print(DEBUG, "Eingegebenerer Satz:")
    # print(sentences, "\n")

    # get the words of each sentence
    # for sentence in sentences:
    #     words = nltk.word_tokenize(sentence)
    #     print(words)
    # print("\n")

    # Chatbot Answer
    loadingAnimation(2, 1)
    chatbotAnswer("Boah, sorry. Das weiß ich auch nicht.")
