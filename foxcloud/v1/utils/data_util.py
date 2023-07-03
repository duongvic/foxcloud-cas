
import fnmatch
import jmespath
import re
import six
import sre_constants
import uuid

from functools import wraps
import inspect

from foxcloud import log as _log
from foxcloud import exceptions as exc
import math


def valid_kwargs(*valid_args):
    """
    Check if argument passed as **kwargs to a function are
    present in valid_args
    Typically, valid_kwargs is used when we want to distinguish
    between none and omitted arguments and we still want to validate
    the argument list

    Usage
    @valid_kwargs('flavor_id', 'image_id')
    def my_func(self, arg1, arg2, **kwargs):
        ...

    :param valid_args:
    :return:
    """

    def wrapper(func):
        """

        :param func:
        :return:
        """

        @wraps(func)
        def func_wrapper(*args, **kwargs):
            all_args = inspect.getfullargspec(func)
            for k in kwargs:
                if k not in all_args.args[1:] and k not in valid_args:
                    raise TypeError(
                        "{f}() got an unexpected keyword argument "
                        "'{arg}'".format(f=inspect.stack()[1][3], arg=k)
                    )
            return func(*args, **kwargs)

        return func_wrapper

    return wrapper


def _filter_list(data, name_or_id, filters):
    """Filter a list by name/ID and arbitrary meta data.

    :param list data:
        The list of dictionary data to filter. It is expected that
        each dictionary contains an 'id' and 'name'
        key if a value for name_or_id is given.
    :param string name_or_id:
        The name or ID of the entity being filtered. Can be a glob pattern,
        such as 'nb01*'.
    :param filters:
        A dictionary of meta data to use for further filtering. Elements
        of this dictionary may, themselves, be dictionaries. Example::

            {
              'last_name': 'Smith',
              'other': {
                  'gender': 'Female'
              }
            }
        OR
        A string containing a jmespath expression for further filtering.
    """
    # The logger is shade.fmmatch to allow a user/operator to configure logging
    # not to communicate about fnmatch misses (they shouldn't be too spammy,
    # but one never knows)
    log = _log.setup_logging('shade.fnmatch')
    if name_or_id:
        # name_or_id might already be unicode
        name_or_id = _make_unicode(name_or_id)
        identifier_matches = []
        bad_pattern = False
        try:
            fn_reg = re.compile(fnmatch.translate(name_or_id))
        except sre_constants.error:
            # If the fnmatch re doesn't compile, then we don't care,
            # but log it in case the user DID pass a pattern but did
            # it poorly and wants to know what went wrong with their
            # search
            fn_reg = None
        for e in data:
            e_id = _make_unicode(e.get('id', None))
            e_name = _make_unicode(e.get('name', None))

            if ((e_id and e_id == name_or_id) or
                    (e_name and e_name == name_or_id)):
                identifier_matches.append(e)
            else:
                # Only try fnmatch if we don't match exactly
                if not fn_reg:
                    # If we don't have a pattern, skip this, but set the flag
                    # so that we log the bad pattern
                    bad_pattern = True
                    continue
                if ((e_id and fn_reg.match(e_id)) or
                        (e_name and fn_reg.match(e_name))):
                    identifier_matches.append(e)
        if not identifier_matches and bad_pattern:
            log.debug("Bad pattern passed to fnmatch", exc_info=True)
        data = identifier_matches

    if not filters:
        return data

    if isinstance(filters, six.string_types):
        return jmespath.search(filters, data)

    def _dict_filter(f, d):
        if not d:
            return False
        for key in f.keys():
            if isinstance(f[key], dict):
                if not _dict_filter(f[key], d.get(key, None)):
                    return False
            elif d.get(key, None) != f[key]:
                return False
        return True

    filtered = []
    for e in data:
        filtered.append(e)
        for key in filters.keys():
            if isinstance(filters[key], dict):
                if not _dict_filter(filters[key], e.get(key, None)):
                    filtered.pop()
                    break
            elif e.get(key, None) != filters[key]:
                filtered.pop()
                break
    return filtered


def _make_unicode(input):
    """Turn an input into unicode unconditionally

    :param input:
       A unicode, string or other object
    """
    try:
        if isinstance(input, unicode):
            return input
        if isinstance(input, str):
            return input.decode('utf-8')
        else:
            # int, for example
            return unicode(input)
    except NameError:
        # python3!
        return str(input)


def _get_entity(cloud, resource, name_or_id, filters, **kwargs):
    """Return a single entity from the list returned by a given method.

    :param object cloud:
        The controller class (Example: the main OpenStackCloud object) .
    :param string or callable resource:
        The string that identifies the resource to use to lookup the
        get_<>_by_id or search_<resource>s methods(Example: network)
        or a callable to invoke.
    :param string name_or_id:
        The name or ID of the entity being filtered or an object or dict.
        If this is an object/dict with an 'id' attr/key, we return it and
        bypass resource lookup.
    :param filters:
        A dictionary of meta data to use for further filtering.
        OR
        A string containing a jmespath expression for further filtering.
        Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
    """

    # Sometimes in the control flow of shade, we already have an object
    # fetched. Rather than then needing to pull the name or id out of that
    # object, pass it in here and rely on caching to prevent us from making
    # an additional call, it's simple enough to test to see if we got an
    # object and just short-circuit return it.

    if (hasattr(name_or_id, 'id') or
       (isinstance(name_or_id, dict) and 'id' in name_or_id)):
        return name_or_id

    # If a uuid is passed short-circuit it calling the
    # get_<resorce_name>_by_id method
    if getattr(cloud, 'use_direct_get', False) and _is_uuid_like(name_or_id):
        get_resource = getattr(cloud, 'get_%s_by_id' % resource, None)
        if get_resource:
            return get_resource(name_or_id)

    search = resource if callable(resource) else getattr(
        cloud, 'search_%ss' % resource, None)
    if search:
        entities = search(name_or_id, filters, **kwargs)
        if entities:
            if len(entities) > 1:
                raise exc.OpenStackCloudException(
                    "Multiple matches found for %s" % name_or_id)
            return entities[0]
    return None


def _is_uuid_like(val):
    """Returns validation of a value as a UUID.

    :param val: Value to verify
    :type val: string
    :returns: bool

    .. versionchanged:: 1.1.1
       Support non-lowercase UUIDs.
    """
    try:
        return str(uuid.UUID(val)).replace('-', '') == _format_uuid_string(val)
    except (TypeError, ValueError, AttributeError):
        return False


def _format_uuid_string(string):
    return (string.replace('urn:', '')
                  .replace('uuid:', '')
                  .strip('{}')
                  .replace('-', '')
                  .lower())


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])
