from importlib import import_module


class Server(object):
    def __init__(self, path):
        try:
            mod_models = import_module('%s.models' % path)
        except ImportError as err:
            err.msg += ". See the docs."
            raise

        for model_class in mod_models.model_classes:
            print('{0[name]} -> {0[pk_field]}'.format(model_class))
