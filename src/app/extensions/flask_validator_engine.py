# pylint: disable=unused-argument
import re
from datetime import datetime
from functools import wraps
from flask import request
from werkzeug.exceptions import HTTPException

EXTENSION_NAME = "flask-validator-engine"


class ValidatorEngine(object):
    """ Flask ValidatorEngine is an extension to validate flask request data.

    It allows to validate json payloads, query string parameters, files, and request headers.

    The library uses function decorator pattern, which means the incomming request data is validated before the request hit the flask route function
    When there is a validation error, library raise a ValidationError(werkzeug.exeptions.HTTPException)

    Using the validator object

    Decorate your route function with the validator object like this.

    @validator(<where-to-check-for-data>, <validation-logic>)

    so you have:

    @validator('query_string', {
        'type': ['required', 'alphanumeric']
    })

    The first argument to the validator decorator is the place where you want the validator to check for incoming data "json", "query_string", "headers".

    The second argument is a dictionary holding the validation rules.

    {<Field to validate>: [<Rules: A list if the validation rules to check on the specified field>]}

    Buil-in Validation Rules
        >>> json: using the json rule, the validator expects a JSON object from the client. It validates fields in JSON data.
        >>> query_string: the query_string rule validates the URL query arguments passed by the client.
        >>> headers: validates the request headers
    Built-in Validation Rules Args
        >>> required: Specify a required value.
        >>> max: The maximum character for a parameter.
        >>> min: The mainimum character for a parameter.
        >>> alpha: This check that the input under validation contains only alphabets (A-Za-z).
        >>> alphanumeric: This check that the input under validation contains both alphabets and numbers (A-Za-z0-9).
        >>> list: This check that the input under validation is a list. You can also set your validation to make sure the list is of a specific length

                @validator('json', {
                    'properties': ['list:4']
                })

        >>> integer: This check that the input under validation is an integer.
        >>> float: This check that the input under validation is a float.
        >>> email: This check that the input matches an email regex.
        >>> boolean: This check that the input under validation is a boolean value (True/False) or (1/0)
        >>> regex: This check that the input under validation match against regex pattern

                @validator('json', {
                    'abc-123-XYZ': [r'regex:[\\w\\d\\-]+']
                })

        >>> date: This check that the input under validation is a date that matches the <format> provided.

                @validator('json', {
                    'expiry_date': ['date:%Y/%m/%d %H:%M:%S']
                })

            You can also validate that the date matches the format and that date value sepecified

                @validator('json', {
                    'expiry_date': ['date:%Y/%m/%d,2020/08/30']
                })

        >>> date_before: Checks that the date matches the format and is before the date value specified

                @validator('json', {
                    'expiry_date': ['date_before:%Y/%m/%d %H:%M:%S,2020/01/01 01:02:45']
                })
        >>> date_before_or_equal: Checks that the date matches the format and is before or equals to the date value specified

                @validator('json', {
                    'expiry_date': ['date_before_or_equal:%Y/%m/%d %H:%M:%S,2020/01/01 01:02:45']
                })

        >>> date_after: Checks that the date matches the format and is after the date value specified

                @validator('json', {
                    'expiry_date': ['date_after:%Y/%m/%d %H:%M:%S,2020/01/01 01:02:45']
                })
        >>> date_after_or_equal: Checks that the date matches the format and is after or equals to the date value specified

                @validator('json', {
                    'expiry_date': ['date_after_or_equal:%Y/%m/%d %H:%M:%S,2020/01/01 01:02:45']
                })

    @credits https://github.com/adekoder/flask-validator
    """

    def __init__(self, app=None):

        self.errors = {}

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

    def reset(self):
        """ Empty errors dictionary"""
        self.errors = {}

    def __call__(self, validation_type, rules):

        def wrapper(func):

            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                try:
                    validation_type_method = self.__getattribute__(
                        validation_type)
                    all_validation_passes = validation_type_method(rules)
                    if not all_validation_passes:
                        return self.response()
                    return func(*args, **kwargs)
                except AttributeError:
                    raise Exception(
                        f'AttributeError {validation_type} passed, expecting json or form_data or query_string or headers'
                    ) from AttributeError

            return inner_wrapper

        return wrapper

    def check_values(self, data, validation_rules):
        for field, rules in validation_rules.items():
            for rule in rules:
                validator_name, validator_args = self.rule_splitter(rule)
                try:
                    validation_result = getattr(Validators, validator_name)(
                        data.get(field, None), *validator_args)
                except KeyError:
                    raise Exception(
                        f"{validator_name} - Built-in validator specified not known"
                    ) from KeyError

                if not validation_result['status']:
                    self.add_error(field, validation_result['message'])
                    break

    @staticmethod
    def rule_splitter(data):
        rules = data.split(':', 1)
        validator = rules[0]
        if not len(rules) > 1:
            return validator, []
        args = tuple((
            rules[1], ) if validator == 'regex' else rules[1].split(','))
        return validator, args

    def json(self, rules):
        return self.validate(request.get_json(force=True), rules)

    def query_string(self, rules):
        return self.validate(request.args.to_dict(), rules)

    def headers(self, rules):
        return self.validate(request.headers, rules)

    def files(self, rules):
        return self.validate(request.files.to_dict(), rules)

    def validate(self, data, rules):
        self.check_values(data, rules)
        return not self.has_errors()

    def response(self):
        raise ValidationError(messages=self.errors,
                              description='Validation errors')

    def add_error(self, field, message):
        self.errors[field] = [message]

    def has_errors(self):
        return True if self.errors else False


class Validators():

    @staticmethod
    def required(request_data, *validation_args):  # pylint: disable=unused-argument
        error_msg = 'This field is required'

        if request_data in (None, ''):
            return {
                'status': False,
                'message': error_msg,
            }

        return {
            'status': True,
        }

    @staticmethod
    def max(request_data, *validator_args):
        error_msg = 'This field must not be greater than {args}'.format(
            args=validator_args[0])
        if isinstance(request_data, int):
            if request_data > int(validator_args[0]):
                return {
                    'status': False,
                    'message': error_msg,
                }
        else:
            if len(request_data) > int(validator_args[0]):
                return {
                    'status': False,
                    'message': error_msg,
                }
        return {
            'status': True,
        }

    @staticmethod
    def min(request_data, *validator_args):
        error_msg = 'This field must not be less than {args}'.format(
            args=validator_args[0])
        if isinstance(request_data, int):
            if request_data < int(validator_args[0]):
                return {'status': False, 'message': error_msg}
        else:
            if len(request_data) < int(validator_args[0]):
                return {'status': False, 'message': error_msg}
        return {'status': True}

    @staticmethod
    def alpha(request_data, *validator_args):  # pylint: disable=unused-argument
        error_msg = 'This field must contain an alphabets (A-Za-z)'
        if not request_data.isalpha():
            return {'status': False, 'message': error_msg}
        return {'status': True}

    @staticmethod
    def alphanumeric(request_data, *validator_args):  # pylint: disable=unused-argument
        error_msg = 'This field must contain both alphabets and numbers (A-Za-z0-9)'
        if not request_data.isalnum():
            return {'status': False, 'message': error_msg}
        return {'status': True}

    @staticmethod
    def email(request_data, *validator_args):
        error_msg = 'This field must contain a valid email address'
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

        if not re.search(regex, request_data):
            return {'status': False, 'message': error_msg}
        return {'status': True}

    @staticmethod
    def integer(request_data, *validator_args):  # pylint: disable=unused-argument
        error_msg = 'This field must contain an integer'
        if not isinstance(request_data, int):
            return {'status': False, 'message': error_msg}
        return {'status': True}

    @staticmethod
    def float(request_data, *validator_args):  # pylint: disable=unused-argument
        error_msg = 'This field must contain an float'
        if not isinstance(request_data, float):
            return {'status': False, 'message': error_msg}
        return {'status': True}

    @staticmethod
    def list(request_data, *validator_args):
        error_msg = 'This field must be a list'
        if not isinstance(request_data, list):
            return {'status': False, 'message': error_msg}
        if validator_args:
            if validator_args[0] and len(request_data) != validator_args[0]:
                error_msg += ' with length of {arg}'.format(
                    arg=validator_args[0])
                return {'status': False, 'message': error_msg}

        return {'status': True}

    @staticmethod
    def boolean(request_data, *validator_arg):  # pylint: disable=unused-argument
        error_msg = 'This field must be a boolean value (True/False) or (1/0)'

        if isinstance(request_data, bool) or (request_data
                                              == 0) or request_data == 1:
            return {'status': True}

        return {'status': False, 'message': error_msg}

    @staticmethod
    def regex(request_data, *validator_arg):
        error_msg = 'This field does not match required pattern'
        pattern = validator_arg[0]

        if hasattr(re, 'fullmatch'):
            match = re.fullmatch(pattern, request_data)
        elif not (pattern.startswith('^') and pattern.endswith('$')):
            pattern = '{}{}{}'.format('^', pattern, '$')
            match = re.match(pattern, request_data)
        else:
            match = re.match(pattern, request_data)

        return {
            'status': True
        } if match else {
            'status': False,
            'message': error_msg
        }

    @staticmethod
    def date(request_data, *args):
        error_msg = 'This field must be a date that match this format {arg}'\
            .format(arg=args[0])
        try:
            date_value_1 = datetime.strptime(request_data, args[0])
        except ValueError:
            return {'status': False, 'message': error_msg}

        if len(args) == 2:
            date_value_2 = datetime.strptime(args[1], args[0])
            if date_value_1 != date_value_2:
                error_msg += 'and value must be {arg}'.format(arg=args[1])
                return {'status': False, 'message': error_msg}

        return {'status': True}

    @staticmethod
    def after(request_data, *args):
        if len(args) != 2:
            raise Exception(
                'ArgumentError - Usage should be date_after:<format>,<value>')

        error_msg = 'This field must be after this date {arg}'\
        .format(arg=args[0])

        try:
            date_value_1 = datetime.strptime(request_data, args[0])
        except ValueError:
            return {'status': False, 'message':            \
                'This field must be a date that match this format'.format(arg=args[0])}

        date_value_2 = datetime.strptime(args[1], args[0])
        if date_value_1 <= date_value_2:
            return {'status': False, 'message': error_msg}

        return {'status': True}

    @staticmethod
    def after_or_equal(request_data, *args):
        if len(args) != 2:
            raise Exception(
                'ArgumentError Usage should be date_after_or_equal:<format>,<value>'
            )

        error_msg = 'This field must be after or equal to this date {arg}'\
        .format(arg=args[0])

        try:
            date_value_1 = datetime.strptime(request_data, args[0])
        except ValueError:
            return {'status': False, 'message':            \
                'This field must be a date that match this format'.format(arg=args[0])}

        date_value_2 = datetime.strptime(args[1], args[0])
        if date_value_1 < date_value_2:
            return {'status': False, 'message': error_msg}

        return {'status': True}

    @staticmethod
    def before(request_data, *args):
        if len(args) != 2:
            raise Exception(
                'ArgumentError - Usage should be date_before:<format>,<value>')

        error_msg = 'This field must be before this date {arg}'\
        .format(arg=args[0])

        try:
            date_value_1 = datetime.strptime(request_data, args[0])
        except ValueError:
            return {'status': False, 'message':            \
                'This field must be a date that match this format'.format(arg=args[0])}

        date_value_2 = datetime.strptime(args[1], args[0])
        if date_value_1 >= date_value_2:
            return {'status': False, 'message': error_msg}

        return {'status': True}

    @staticmethod
    def before_or_equal(request_data, *args):
        if len(args) != 2:
            raise Exception(
                'ArgumentError - Usage should be date_before_or_equal:<format>,<value>'
            )

        error_msg = 'This field must be before or equal to this date {arg}'\
        .format(arg=args[0])

        try:
            date_value_1 = datetime.strptime(request_data, args[0])
        except ValueError:
            return {'status': False, 'message':            \
                'This field must be a date that match this format'.format(arg=args[0])}

        date_value_2 = datetime.strptime(args[1], args[0])
        if date_value_1 > date_value_2:
            return {'status': False, 'message': error_msg}

        return {'status': True}


class ValidationError(HTTPException):

    def __init__(self,
                 code: str = 'ValidationError',
                 description: str = None,
                 status_code: int = 400,
                 messages: str = None):

        super().__init__()
        self.status_code = status_code
        self.code = code
        self.description = description
        self.messages = messages
