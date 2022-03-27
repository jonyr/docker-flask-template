from itsdangerous import (
    URLSafeTimedSerializer,
    Signer,
)
from flask import url_for

EXTENSION_NAME = 'flask-serializer-manager'


class SerializerManager(object):

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app: 'Flask'):
        self.app = app
        secret_key = app.config['SECRET_KEY']
        salt = app.config['SECRET_KEY_SALT']
        self.signer = Signer(secret_key, salt=salt)
        self.serializer = URLSafeTimedSerializer(secret_key, salt=salt)

        app.extensions = getattr(app, "extensions", {})
        app.extensions[EXTENSION_NAME] = self

    def encode(self, payload: dict) -> str:
        """Serialize and sign the payload returning an url-safe-string.
        :param payload: a dictionary or a string
        :returns: a signed and serialized url safe string.
        """
        return self.serializer.dumps(payload)

    def decode(self, token: str, expiration: int = 3600) -> str:
        """
        Decode an url-safe-timed-encoded token.
        :param token: A token.
        :param expiration: Token expiration in seconds
        :exception: itsdangerous.exc.BadSignature: When signature does not match
        :returns: a string
        """
        return self.serializer.loads(token, max_age=expiration)

    def sign(self, text: str) -> str:
        """Attach a signature to a specific string
        :param text: A string to be signed
        :returns: A signed string.
        """
        return self.signer.sign(text)

    def unsign(self, signed_text: str) -> str:
        """
        Validate a signed string.
        :param signed_text: A signed string.
        :exception: itsdangerous.exc.BadSignature: When signature does not match
        :returns: a string
        """

        return self.signer.unsign(signed_text)

    def generate_url(self, endpoint: str, token: str) -> str:
        return url_for(endpoint, token=token, _external=True)
