from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import MetaData

from src.app.extensions.flask_exception_handler import \
    ExceptionHandler as ExceptionHandlerClass
from src.app.extensions.flask_response_manager import \
    ResponseManager as ResponseManagerClass
from src.app.extensions.flask_schema_manager import \
    SchemaManager as SchemaManagerClass
from src.app.extensions.flask_serializer_manager import \
    SerializerManager as SerializerManagerClass
from src.app.extensions.flask_validator_engine import ValidatorEngine

metadata = MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(column_0_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    })

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
cors = CORS()
validator = ValidatorEngine()
ExceptionHandler = ExceptionHandlerClass()
ma = Marshmallow()
jwt = JWTManager()
ResponseManager = ResponseManagerClass()
SchemaManager = SchemaManagerClass()
SerializerManager = SerializerManagerClass()


def register_extensions(app: 'Flask') -> None:
    """Register 0 or more extensions mutating the flask app passed in.

    Args:
        app (Flask): Flask application instance
    """
