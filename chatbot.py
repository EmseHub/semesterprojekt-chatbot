# setup (import modules)
import nltk
# nltk.download('punkt')

# constants
WELCOME = "Hello and welcome. I'm a chatbot. Chat with me!"
EXIT_MESSAGES = ['x','exit', 'leave', 'stop', 'break', 'abbrechen', 'verlassen', 'beenden']

# start chat loop with welcome message
print(WELCOME)
while(True):
    # read users input and check for exit intent
    text = input('')
    if str(text).lower() in EXIT_MESSAGES:
        break
    
    # tokenize the users input text
    sentences = nltk.sent_tokenize(text)
    print(sentences)

    # get the words of each sentence
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        print(words)
    
