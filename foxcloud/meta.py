import munch
import ipaddress
import six
import socket

NON_CALLABLES = (six.string_types, bool, dict, int, float, list, type(None))


def obj_to_munch(obj):
    """ Turn an object with attributes into a dict suitable for serializing.
    Some of the things that are returned in OpenStack are objects with
    attributes. That's awesome - except when you want to expose them as JSON
    structures. We use this as the basis of get_hostvars_from_server above so
    that we can just have a plain dict of all of the values that exist in the
    shade metadata for a server.
    """
    if obj is None:
        return None
    elif isinstance(obj, munch.Munch) or hasattr(obj, 'mock_add_spec'):
        # If we obj_to_munch twice, don't fail, just return the munch
        # Also, don't try to modify Mock objects - that way lies madness
        return obj
    elif isinstance(obj, dict):
        # The new request-id tracking spec:
        # https://specs.openstack.org/openstack/nova-specs/specs/juno/approved/log-request-id-mappings.html
        # adds a request-ids attribute to returned objects. It does this even
        # with dicts, which now become dict subclasses. So we want to convert
        # the dict we get, but we also want it to fall through to object
        # attribute processing so that we can also get the request_ids
        # data into our resulting object.
        instance = munch.Munch(obj)
    else:
        instance = munch.Munch()

    for key in dir(obj):
        try:
            value = getattr(obj, key)
        # some attributes can be defined as a @propierty, so we can't assure
        # to have a valid value
        # e.g. id in python-novaclient/tree/novaclient/v2/quotas.py
        except AttributeError:
            continue
        if isinstance(value, NON_CALLABLES) and not key.startswith('_'):
            instance[key] = value
    return instance


obj_to_dict = obj_to_munch


def obj_list_to_munch(obj_list):
    """Enumerate through lists of objects and return lists of dictonaries.
    Some of the objects returned in OpenStack are actually lists of objects,
    and in order to expose the data structures as JSON, we need to facilitate
    the conversion to lists of dictonaries.
    """
    return [obj_to_munch(obj) for obj in obj_list]


obj_list_to_dict = obj_list_to_munch


def get_and_munchify(key, data):
    """Get the value associated to key and convert it.

    The value will be converted in a Munch object or a list of Munch objects
    based on the type
    """
    if key:
        result = data.get(key, []) if key else data
    else:
        result = data

    if isinstance(result, list):
        return obj_list_to_munch(result)
    elif isinstance(result, dict):
        return obj_to_munch(result)
    return result