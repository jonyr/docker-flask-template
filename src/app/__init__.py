import os

from flask import render_template, send_from_directory, url_for

from .factory import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():

    return render_template('newsletter.html')


@app.route("/json")
def json():
    return {
        'status': True,
        'message': 'Everything is working fine',
    }
