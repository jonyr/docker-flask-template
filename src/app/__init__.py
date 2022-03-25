from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():

    return render_template('newsletter.html')


@app.route("/json")
def json():
    return {
        'status': True,
        'message': 'Everything is working fine',
    }
