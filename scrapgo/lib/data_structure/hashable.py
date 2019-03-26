import functools
from collections import UserDict, abc


class HashableDict(UserDict):

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def kwargs2hashable(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for key, arg in kwargs.items():
            if arg and isinstance(arg, abc.Mapping):
                kwargs[key] = HashableDict(arg)
        return func(*args, **kwargs)
    return wrapper
