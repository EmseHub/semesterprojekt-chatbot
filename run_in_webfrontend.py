from flask import Flask, render_template, request, jsonify, json
from chatbot import get_response


app = Flask(
    __name__,
    template_folder="webfrontend",
    static_folder="webfrontend"
)


@app.get("/")
def index():
    # Aufruf der Startseite/Chatbot
    return render_template("index.html")


@app.post("/start")
def start():
    response, diagnostic, is_data_changed, students, courses = get_response(
        "Start"
    )
    reply = {
        "request": "Start",
        "response": "",
        "diagnostic": {},
        "is_data_changed": True,
        "data_students": students,
        "data_courses": courses
    }
    return jsonify(reply)


@app.post("/response")
def response():
    data = json.loads(request.data)
    message = data["message"]

    if (not message.strip()):
        return None

    response, diagnostic, is_data_changed, students, courses = get_response(
        message
    )

    reply = {
        "request": message,
        "response": response,
        "diagnostic": diagnostic,
        "is_data_changed": is_data_changed,
        "data_students": students,
        "data_courses": courses
    }

    # JS-Objekt mit der fertigen Antwort zurück ans Frontend geben
    # return render_template("index.html", reply=jsonify(reply))
    return jsonify(reply)


if (__name__) == "__main__":
    app.run(debug=True)
