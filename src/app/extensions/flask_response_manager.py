from flask import make_response, jsonify, request
from flask_sqlalchemy import Pagination

EXTENSION_NAME = "flask-response-manager"


class ResponseManager(object):

    def __init__(self, app=None):

        self.response = None
        self.status_code = None
        self.errors = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: 'Flask'):
        self.app = app

        app.extensions = getattr(app, "extensions", {})
        app.extensions[EXTENSION_NAME] = self

        @app.teardown_appcontext
        def teardown_response_service(response_or_exc):  # pylint: disable=unused-variable
            self.reset()
            return response_or_exc

    def build(self, data, code: int = None, pagination: Pagination = None):
        _response = {}
        _response['data'] = data
        _response['errors'] = None
        if pagination:
            _response['pagination'] = self.build_pagination(pagination)
        self.response = make_response(jsonify(_response))
        return self.response, self.set_status_code(code)

    def build_error(self, error, code: int = 500):
        _response = {}
        _response['data'] = None
        _response['errors'] = error
        self.response = make_response(jsonify(_response))
        return self.response, code

    def set_status_code(self, code: int = None):

        http_status_codes = {
            'GET': 200,
            'POST': 201,
            'PUT': 200,
            'PATCH': 200,
            'DELETE': 204,
        }
        return code or http_status_codes.get(request.method, 200)

    def build_pagination(self, pagination):

        if isinstance(pagination, (Pagination, )):

            # self.response.headers['X-Pagination'] = {
            #     'prev_page':
            #     pagination.prev_num if pagination.prev_num else False,
            #     'next_page':
            #     pagination.next_num if pagination.next_num else False,
            #     'page': pagination.page,
            #     'per_page': pagination.per_page,
            #     'pages': pagination.pages,
            #     'total': pagination.total
            # }

            return {
                'prev_page':
                pagination.prev_num if pagination.prev_num else False,
                'next_page':
                pagination.next_num if pagination.next_num else False,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages,
                'total': pagination.total
            }

    def reset(self):
        self.response = None
        self.status_code = None
        self.errors = None
