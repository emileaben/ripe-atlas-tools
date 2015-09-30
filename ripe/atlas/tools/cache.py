import cPickle as pickle
import datetime
import dbm
import functools
import os


class LocalCache(object):
    """
    Simple caching engine, making use of the built-in dbm support.  This will
    create a file called cache.db in ripe-atlas-tools config directory and dump
    stuff in there for use later.
    """

    def __init__(self):
        self._now = datetime.datetime.now()
        self._db = dbm.open(self._get_db_path(), "c")

    def __contains__(self, key):
        return key in self._db

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value, expires=None):
        self._db[key] = pickle.dumps((expires, value))

    def __delitem__(self, key):
        if key not in self._db:
            raise KeyError
        del self._db[key]

    def keys(self):
        return self._db.keys()

    def items(self):
        for key in self.keys():
            yield key, self._db[key]

    def get(self, key, default=None):
        if key in self._db:
            expires, value = pickle.loads(self._db[key])
            if not expires or expires > self._now:
                return value
            else:
                del(self._db[key])
        return default

    def set(self, key, value, expires=None):
        return self.__setitem__(
            key, value, self._now + datetime.timedelta(seconds=expires))

    def clear(self, key=None):
        """
        Removes a specific key from the cache manually, or will wipe the entire
        cache if you don't specify `key`.  Note that this shouldn't be necessary
        unless you've cached something with an inappropriately long expire time.
        """
        if key:
            if key in self._db:
                del(self._db[key])
        else:
            for key in self.keys():
                del(self._db[key])

    def expire(self):
        """
        Clears out should-be-expired values from the cache.  Note that this
        happens automatically whenever you call `.get()` so you should never
        really need to run this.
        """
        for key in self.keys():
            self.get(key)

    @staticmethod
    def _get_db_path():
        if "HOME" in os.environ:
            return os.path.join(
                os.environ["HOME"], ".config", "ripe-atlas-tools", "cache.db")
        return os.path.join("/", "tmp", "cache.db")

cache = LocalCache()


class Memoiser(object):
    """
    Enabling class for the @memoised decorator
    """

    def __init__(self, function, cache_time):
        self._function = function
        self._cache_time = cache_time

    def __call__(self, *args, **kwargs):

        key = pickle.dumps([args, kwargs])
        value = cache[key]

        if value:
            return value

        value = self._function(*args, **kwargs)
        cache.set(key, value, self._cache_time)

        return value

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def memoised(cache_time):
    """
    Decorate a method or function with this to cache the result of said method
    for n seconds:

    @memoised(60 * 60)  # Cache for one hour
    my_function(some_arguments):
        ...
        return whatever
    """
    def _wrap(function):
        return Memoiser(function, cache_time=cache_time)
    return _wrap