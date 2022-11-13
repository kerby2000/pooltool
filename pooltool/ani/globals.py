from direct.showbase import ShowBaseGlobal

from pooltool.error import ConfigError


def is_showbase_initialized() -> bool:
    """Return whether ShowBase has been initialized

    Checks by seeing whether `base` is an attribute of the ShowBaseGobal namespace,
    which is dynamically added when ShowBase is initialized:

    https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBaseGlobal#module-direct.showbase.ShowBaseGlobal
    """
    return True if hasattr(ShowBaseGlobal, "base") else False


def require_showbase(func):
    """Return wrapper that complains if ShowBase no instance exists"""

    def wrapper(*args, **kwargs):
        if is_showbase_initialized():
            return func(*args, **kwargs)

        raise ConfigError(
            f"ShowBase instance has not been initialized, but a function has been "
            f"called that requires it: '{func.__name__}'."
        )

    return wrapper


class _Global:
    """A namespace for shared variables

    When an instance of ShowBase is created, Panda3d populates the global namespace with
    many variables so they can be accessed from anywhere. But to those unfamiliar with
    this design idiom, tracking the origin of these variables is extremely confusing.
    Fortunately, Panda3d provides a module, `ShowBaseGlobal`, that you can use to access
    these variables the _right_ way:

    https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBaseGlobal#module-direct.showbase.ShowBaseGlobal

    With that in mind, this class is designed for two things:

        (1) It gives access to the `ShowBaseGlobal` variables.
        (2) It provide a namespace for other variables designed to be shared across many
            modules. Such variables must be set with the `register` method.
    """

    _freeze = False

    clock = ShowBaseGlobal.globalClock
    aspect2d = ShowBaseGlobal.aspect2d
    render2d = ShowBaseGlobal.render2d

    def __init__(self):
        self._custom_registry = set()
        self._freeze = True

    def __setattr__(self, key, val):
        if self._freeze and not hasattr(self, key):
            raise TypeError(
                "Global is a sacred namespace and does not support direct attribute "
                "declaration. Please use the Global.register method."
            )

        object.__setattr__(self, key, val)

    @property
    @require_showbase
    def base(self):
        return ShowBaseGlobal.base

    @property
    @require_showbase
    def render(self):
        return ShowBaseGlobal.base.render

    @property
    @require_showbase
    def task_mgr(self):
        return ShowBaseGlobal.base.taskMgr

    @property
    @require_showbase
    def loader(self):
        return ShowBaseGlobal.base.loader

    def register(self, name, var):
        """Register a variable into the Global namespace"""
        self._freeze = False
        setattr(self, name, var)
        self._freeze = True
        self._custom_registry.add(name)


Global = _Global()
