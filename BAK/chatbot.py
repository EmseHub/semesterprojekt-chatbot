"PYTHON CHATBOT Semesterprojekt"
# setup: import outsourced files/functions
from src.constants import *
from src.helpers import *

# import third-party modules
from time import sleep


# start chat loop with welcome message
print(WELCOME)
printAvailableFunctions()
print(DIVIDER)

while True:
    # read users input
    text = studentInput()

    # check if user wants to exit or needs help
    if str(text).lower() in EXIT_MESSAGES:
        print("Tschüss!")
        break
    if str(text).lower() in ["help", "hilfe"]:
        printAvailableFunctions()
        continue

    # NLP PIPELINE
    # preprocessing (tokenization, filter stop words)

    # tokenize the users input text

    # get the words of each sentence

    # remove stopwords

    # pos_tagging (get nouns/verbs / extract features)

    # stemming/lemmatization of the features

    # get results as bag of words

    # get intent by similiarity of intents.data?

    # Chatbot Answer
    # loadingAnimation(2, 3)
    # chatbotAnswer("Boah, sorry. Das weiß ich auch nicht.")

    test()
