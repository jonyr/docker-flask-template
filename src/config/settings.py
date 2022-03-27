import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR')

    # SQL Alchemy Settings
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DB = os.getenv('POSTGRES_DB')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_DEFAULT_MAX_PER_PAGE = 100
    SQLALCHEMY_DEFAULT_PER_PAGE = 25
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True


class TestingConfig(Config):
    FLASK_ENV = 'testing'
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    FLASK_ENV = 'production'


config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)
