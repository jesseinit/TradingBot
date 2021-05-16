import json

from flask import Blueprint, request

listener_blueprint = Blueprint(
    "listener_blueprint", __name__, url_prefix="/api/v1/listener"
)


@listener_blueprint.route("/webhook", methods=["POST"])
def ai_listener():
    ai_response = request.get_json(force=True)
    with open("webhook_response.log", "a") as log_file:
        log_file.write(f"{json.dumps(ai_response)}\n")
    return {"status": "response recieved"}
