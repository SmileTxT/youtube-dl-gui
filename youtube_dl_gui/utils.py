#!/usr/bin/env python2

"""Youtubedlg module that contains util functions.

Attributes:
    RANDOM_OBJECT (object): Object that it's used as a default parameter.

    YOUTUBEDL_BIN (string): Youtube-dl binary filename.

"""


import os
import sys
import subprocess


RANDOM_OBJECT = object()


YOUTUBEDL_BIN = 'youtube-dl'
if os.name == 'nt':
    YOUTUBEDL_BIN += '.exe'


def remove_shortcuts(path):
    """Return given path after removing the shortcuts. """
    path = path.replace('~', os.path.expanduser('~'))
    return path


def absolute_path(filename):
    """Return absolute path to the given file. """
    path = os.path.realpath(os.path.abspath(filename))
    return os.path.dirname(path)


def open_dir(path):
    """Open path using default file navigator. """
    path = remove_shortcuts(path)

    if os.name == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))


def check_path(path):
    """Create path if not exist. """
    if not os.path.exists(path):
        os.makedirs(path)


def get_config_path():
    """Return user config path.

    Note:
        Windows = %AppData%
        Linux   = ~/.config

    """
    if os.name == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = os.path.join(os.path.expanduser('~'), '.config')

    return path


def shutdown_sys(password=''):
    """Shuts down the system.

    Args:
        password (string): SUDO password for linux.

    Note:
        On Linux you need to provide sudo password if you don't
        have elevated privileges.

    """
    if os.name == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if not password:
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            subprocess.Popen(['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                             stdin=subprocess.PIPE).communicate(password + '\n')


def get_time(seconds):
    """Convert given seconds to days, hours, minutes and seconds.

    Args:
        seconds (float): Time in seconds.

    Returns:
        Dictionary that contains the corresponding days, hours, minutes
        and seconds of the given seconds.

    """
    dtime = dict(seconds=0, minutes=0, hours=0, days=0)

    dtime['days'] = int(seconds / 86400)
    dtime['hours'] = int(seconds % 86400 / 3600)
    dtime['minutes'] = int(seconds % 86400 % 3600 / 60)
    dtime['seconds'] = int(seconds % 86400 % 3600 % 60)

    return dtime


def get_icon_file():
    """Search for youtube-dlg app icon.

    Returns:
        The path to youtube-dlg icon file if exists, else returns None.

    Note:
        Paths that get_icon_file() function searches.

        Windows: __main__ directory.
        Linux: __main__ directory, $XDG_DATA_DIRS and /usr/share/pixmaps.

    """
    SIZES = ('256x256', '128x128', '64x64', '48x48', '32x32', '16x16')
    ICON_NAME = 'youtube-dl-gui_%s.png'

    ICONS_LIST = [ICON_NAME % size for size in SIZES]

    # __main__ dir
    path = os.path.join(absolute_path(sys.argv[0]), 'icons')

    for icon in ICONS_LIST:
        icon_file = os.path.join(path, icon)

        if os.path.exists(icon_file):
            return icon_file

    if os.name != 'nt':
        # $XDG_DATA_DIRS/icons
        path = os.getenv('XDG_DATA_DIRS')

        if path is not None:
            for xdg_path in path.split(':'):
                xdg_path = os.path.join(xdg_path, 'icons', 'hicolor')

                for size in SIZES:
                    icon_name = ICON_NAME % size
                    icon_file = os.path.join(xdg_path, size, 'apps', icon_name)

                    if os.path.exists(icon_file):
                        return icon_file

        # /usr/share/pixmaps
        path = '/usr/share/pixmaps'

        for icon in ICONS_LIST:
            icon_file = os.path.join(path, icon)

            if os.path.exists(icon_file):
                return icon_file

    return None


class TwoWayOrderedDict(object):

    """Custom data structure which implements a two way ordrered dictionary.

    TwoWayOrderedDict it's a custom dictionary in which you can get the
    key:value relationship but you can also get the value:key relationship.
    It also remembers the order in which the items were inserted and supports
    almost all the features of the build-in dict.
    
    Note:
        Ways to create a new dictionary.

        *) d = TwoWayOrderedDict(a=1, b=2) (Unordered)
        *) d = TwoWayOrderedDict({'a': 1, 'b': 2}) (Unordered)

        *) d = TwoWayOrderedDict([('a', 1), ('b', 2)]) (Ordered)
        *) d = TwoWayOrderedDict(zip(['a', 'b', 'c'], [1, 2, 3])) (Ordered)

    Examples:
        >>> d = TwoWayOrderedDict(a=1, b=2)
        >>> d['a']
        1
        >>> d[1]
        'a'
        >>> print d
        {'a': 1, 'b': 2}

    """

    def __init__(self, *args, **kwargs):
        self._items = list()
        self._load_into_dict(args, kwargs)

    def __getitem__(self, key):
        try:
            item = self._find_item(key)

            return self._get_value(key, item)
        except KeyError as error:
            raise error

    def __setitem__(self, key, value):
        index = 0

        while index < len(self._items):
            item = self._items[index]

            if (key == item[0] or key == item[1] or
                    value == item[0] or value == item[1]):
                self._items.remove(item)
            else:
                index += 1

        self._items.append((key, value))

    def __delitem__(self, key):
        try:
            item = self._find_item(key)

            self._items.remove(item)
        except KeyError as error:
            raise error

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for item in self._items:
            yield item[0]

    def __contains__(self, item):
        """Return True if the item matches either a
        dictionary key or value else False. """
        try:
            self._find_item(item)
        except KeyError:
            return False

        return True

    def __repr__(self):
        return str(self._items)

    def __str__(self):
        return str(dict(self._items))

    def _get_value(self, key, item):
        """Return the key:value or value:key relationship
        for the given item. """
        if key == item[0]:
            return item[1]

        if key == item[1]:
            return item[0]

    def _find_item(self, key):
        """Search for the item which contains the given key.
        
        This method will compare the key both with the key and the value
        of the item until it finds a match else it will raise a KeyError
        exception.
        
        Returns:
            item (tuple): Tuple which contains the (key, value).
        
        Raises:
            KeyError
        
        """
        for item in self._items:
            if key == item[0] or key == item[1]:
                return item

        raise KeyError(key)

    def _load_into_dict(self, args, kwargs):
        """Load new items into the dictionary. This method handles the
        items insertion for the __init__ and update methods. """
        for item in args:
            if type(item) == dict:
                item = item.items()

            for key, value in item:
                self.__setitem__(key, value)

        for key, value in kwargs.items():
            self.__setitem__(key, value)

    def items(self):
        """Return the item list instead of returning the dict view. """
        return self._items

    def values(self):
        """Return a list with all the values of the dictionary instead of
        returning the dict view for the values. """
        return [item[1] for item in self._items]

    def keys(self):
        """Return a list with all the keys of the dictionary instead of
        returning the dict view for the keys. """
        return [item[0] for item in self._items]

    def get(self, key, default=None):
        """Return the value for key or the key for value if key
        is in the dictionary else default.
        
        Note:
            This method does NOT raise a KeyError.
        
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def pop(self, key, default=RANDOM_OBJECT):
        """If key is in the dictionary remove it and return its value
        else return default. If default is not given and key is not in
        the dictionary a KeyError is raised. """
        try:
            item = self._find_item(key)
            value = self._get_value(key, item)

            self._items.remove(item)
        except KeyError as error:
            if default == RANDOM_OBJECT:
                raise error

            value = default

        return value

    def popitem(self):
        """Remove and return a (key, value) pair from the dictionary.
        If the dictionary is empty calling popitem() raises a KeyError.
        
        Note:
            popitem() is useful to destructively iterate over a dictionary.
        
        Raises:
            KeyError
        
        """
        if len(self._items) == 0:
            raise KeyError('popitem(): dictionary is empty')

        return self._items.pop()

    def setdefault(self, key, default=None):
        """If key is in the dictionary return its value else
        insert a new key with a value of default and return default. """
        try:
            return self.__getitem__(key)
        except KeyError:
            self.__setitem__(key, default)
            return default

    def update(self, *args, **kwargs):
        """Update the dictionary with the (key, value) pairs
        overwriting existing keys.
        
        Example:
            >>d = TwoWayOrderedDict(a=1, b=2)
            >>print d
            {'a': 1, 'b': 2}
            
            >>d.update({'a': 0, 'b': 1, 'c': 2})
            {'a': 0, 'b': 1, 'c': 2}
            
            >>d.update(d=3)
            {'a': 0, 'b': 1, 'c': 2, 'd': 3}
        
        """
        self._load_into_dict(args, kwargs)

    def copy(self):
        """Return a copy of our custom dictionary. """
        return TwoWayOrderedDict(self._items)

    def clear(self):
        """Remove all items from the dictionary. """
        del self._items[:]
