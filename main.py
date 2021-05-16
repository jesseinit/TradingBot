from flask import Flask

from blueprints.wallet.wallet_blueprint import wallet_blueprint
from blueprints.listener.listener_blueprint import listener_blueprint

app = Flask(__name__)

app.register_blueprint(wallet_blueprint)
app.register_blueprint(listener_blueprint)


@app.route("/")
def hello_world():
    return "<p>Hello Carina, what do you want to do today?</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
