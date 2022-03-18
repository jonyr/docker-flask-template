from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():

    return {
        'status': True,
        'message': 'Everything is working fine',
    }
