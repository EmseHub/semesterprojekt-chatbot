from flask import Flask, render_template, request, jsonify, json
# from chatbot import get_response

app = Flask(__name__)


def get_response(message):
    # dummy get_response
    # (von chatbot.py einbinden! aktuell kein Zugriff auf Modul durch Ordnerstruktur)
    return "TEST"


@app.get('/')
def index():
    # Aufruf der Startseite/Chatbot
    return render_template("index.html")


@app.post('/response')
def response():
    # message = request.form.get("message")
    data = json.loads(request.data)
    message = data["message"]

    # TODO: function get_response von chatbot.py einbinden anstatt des dummys
    response = get_response(message)
    reply = {"request": message,
             "response": response,
             "data": {
                 "studentData": {},
                 "diagnostik": {}
             },
             }

    print("Rückgabe vom Backend:", reply)
    # JS-Objekt mit der fertigen Antwort zurück ans Frontend geben
    # return render_template('index.html', reply=jsonify(reply))
    return jsonify(reply)


if (__name__) == "__main__":
    app.run(debug=True)
