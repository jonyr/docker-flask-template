import importlib

EXTENSION_NAME = "flask-schema"


class SchemaManager(object):

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
        pass

    def schema_for(self, model, name=None, **kwargs):
        # Get an instance (create one if it doesn't exist)
        # And then reset it to apply all defaults

        if model is None:
            raise Exception('SchemaError')

        model_name = name or type(model).__name__

        schema_class = f'{model_name}Schema'

        schemas_module = importlib.import_module('iglobal.schemas')
        schema = getattr(schemas_module, schema_class)(**kwargs)

        return schema

    def dump(self, model: object, **kwargs: dict):
        """Serialize an object"""
        return self.schema_for(model, **kwargs).dump(model)

    def load(self, payload, name=None, **kwargs):
        schema = self.schema_for(payload, name=name, **kwargs)
        # kwargs 'many', 'partial' or 'unknown' must to be passed to load
        load_kwargs = {
            key: value
            for key, value in kwargs.items() if key in (
                'instance',
                'many',
                'partial',
                'unknown',
            )
        }

        if kwargs.get('context'):
            schema.context = kwargs.get('context')

        return schema.load(payload, **load_kwargs)
