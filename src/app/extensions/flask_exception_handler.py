# pylint: disable=invalid-name
import traceback
from http import HTTPStatus

from flask import current_app, request
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import HTTPException

EXTENSION_NAME = "flask-exception-handler"


def get_ip_address():
    """ Get the real ip address
    link: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
    """
    if 'X-Forwarded-For' in request.headers:
        proxy_data = request.headers['X-Forwarded-For']
        ip_list = proxy_data.split(',')
        return ip_list[0]  # first address in list is User IP
    else:
        return request.remote_addr  # For local development


class ExceptionHandler(object):

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        app.register_error_handler(
            ValidationError,
            self.handle_validation_errors,
        )

        app.register_error_handler(
            HTTPException,
            self.handle_custom_exceptions,
        )

        app.register_error_handler(
            Exception,
            self.try_catch_all,
        )

        @app.after_request
        def log_request(response):

            if app.config.get('FLASK_ENV') == 'production':
                return response
            if request.path == '/favicon.ico':
                return response
            elif request.path.startswith('/static'):
                return response

            payload = request.get_json()
            args = dict(request.args)

            log_params = [
                ('method', f'[{request.method}] {request.path}'),
                ('status', response.status_code),
                ('params', args),
            ]

            if payload:
                log_params.append(('payload', payload))

            parts = []
            for name, value in log_params:
                parts.append(f"\n{name}={value}")
            line = " ".join(parts)

            app.logger.info(line)

            return response

        app.extensions = getattr(app, "extensions", {})
        app.extensions[EXTENSION_NAME] = self

    def handle_validation_errors(self, error):

        return {
            'data': None,
            'errors': {
                'description': 'Validation errors',
                'type': error.__class__.__name__,
                'details': error.normalized_messages(),
            }
        }, HTTPStatus.BAD_REQUEST

    def handle_custom_exceptions(self, error):

        response = {
            'description': error.description,
            'type': error.__class__.__name__,
        }

        if hasattr(error, 'messages'):
            response['details'] = error.messages

        current_app.logger.error(traceback.format_exc(2))

        return {'data': None, 'errors': response}, error.code

    def try_catch_all(self, error):

        response = {
            'description': str(error),
            'type': error.__class__.__name__,
        }

        current_app.logger.error(traceback.format_exc(2))

        return {
            'data': None,
            'errors': response
        }, HTTPStatus.INTERNAL_SERVER_ERROR
