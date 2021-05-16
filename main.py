import json

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello Carina, what do you want to do today?</p>"


@app.route("/api/v1/listener", methods=["POST"])
def ai_listener():
    ai_response = request.get_json(force=True)

    with open("webhook_response.log", "a") as log_file:
        log_file.write(f"{json.dumps(ai_response)}\n")

    return {"status": "response recieved"}


if __name__ == "__main__":
    app.run(host="0.0.0.0")
