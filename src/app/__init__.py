import os

from flask import render_template, url_for

from .factory import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.route("/")
def index():

    return render_template('newsletter.html')


@app.route("/json")
def json():
    return {
        'status': True,
        'message': 'Everything is working fine',
    }
