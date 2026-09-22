from flask import Flask
from Api.api import route

route2 = Flask(__name__)
route2.register_blueprint(route)

if __name__ == "__main__":
    route2.run(host="0.0.0.0", port=5000)
