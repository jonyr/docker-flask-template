from atexit import register

from flask import Flask

from src.app.extensions import register_extensions
from src.cli import register_cli_commands
from src.config import config_by_name


def create_app(environment: str = 'development',
               settings_override: dict = None):

    app = Flask(__name__)
    app.config.from_object(config_by_name[environment])

    if settings_override:
        app.config.update(settings_override)

    register_cli_commands(app)
    register_extensions(app)

    # with app.app_context():
    #     app.add_url_rule('/favicon.ico',
    #                      redirect_to=url_for('static', filename='favicon.ico'))

    return app
