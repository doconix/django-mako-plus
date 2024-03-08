from importlib import import_module


def qualified_name(obj):
    '''Returns the fully-qualified name of the given object'''
    if not hasattr(obj, '__module__'):
        obj = obj.__class__
    module = obj.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__qualname__
    return '{}.{}'.format(module, obj.__qualname__)


def import_qualified(name):
    '''
    Imports a fully-qualified name from a module:

        cls = import_qualified('homepage.views.index.MyForm')

    Raises an ImportError if it can't be ipmorted.
    '''
    parts = name.rsplit('.', 1)
    if len(parts) != 2:
        raise ImportError('Invalid fully-qualified name: {}'.format(name))
    try:
        return getattr(import_module(parts[0]), parts[1])
    except AttributeError:
        raise ImportError('{} not found in module {}'.format(parts[1], parts[0]))
