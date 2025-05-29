from threading import Lock


class Singleton(type):
    _instances: dict[str, object] = {}

    def __call__(cls, *args, **kwargs):
        key = cls.instance_key()

        with Lock():
            if key not in cls._instances:
                cls._instances[key] = super().__call__(*args, **kwargs)

        return cls._instances[key]

    def instance_key(cls):
        return super().__name__
