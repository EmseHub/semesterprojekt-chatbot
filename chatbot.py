from nlp_pipelines import nltk_pipeline


def getResponse(message):
    return nltk_pipeline.get_tokenized_text(message)


# Input via Terminal (später ersetzt durch String vom Frontend)
while True:
    # message = input()
    # print("Eingabe:\n" + message)
    # if message.lower() == "exit":
    #     break

    sample_message = "Das ist eine Beispiel-Nachricht, Aber mit Fehlren und  Leerzeichen. Sie wurde z.B. verfasst von Dr. House und Mr. X, während der Hg. Homer ist."

    response = getResponse(sample_message.strip())
    # print(response)
    break
