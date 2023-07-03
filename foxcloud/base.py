import copy
import munch

from oslo_utils import strutils

SUPPORTED_ENGINES = ['heat', 'console']


def getid(obj):
    """Get object's ID or object.
    Abstracts the common pattern of allowing both an object or an object's ID
    as a parameter when dealing with relationships.
    """
    return getattr(obj, 'id', obj)


class HookableMixin(object):
    """Mixin so classes can register and run hooks."""
    _hooks_map = {}

    @classmethod
    def add_hook(cls, hook_type, hook_func):
        """Add a new hook of specified type.
        :param cls: class that registers hooks
        :param hook_type: hook type, e.g., '__pre_parse_args__'
        :param hook_func: hook function
        """
        if hook_type not in cls._hooks_map:
            cls._hooks_map[hook_type] = []

        cls._hooks_map[hook_type].append(hook_func)

    @classmethod
    def run_hooks(cls, hook_type, *args, **kwargs):
        """Run all hooks of specified type.
        :param cls: class that registers hooks
        :param hook_type: hook type, e.g., '__pre_parse_args__'
        :param args: args to be passed to every hook function
        :param kwargs: kwargs to be passed to every hook function
        """
        hook_funcs = cls._hooks_map.get(hook_type) or []
        for hook_func in hook_funcs:
            hook_func(*args, **kwargs)


class BaseManager(HookableMixin):
    """Manager for API services.
    Managers interact with a particular type of API (Neutron, Nova, Cinder, Octavia,..)
    and provide operations for them.
    """
    resource_class = None

    def __init__(self, name_or_id, api_version, session=None, engine='console', endpoint=None, **kwargs):
        """Initializes BaseManager with `client`.
        :param name_or_id: Name or ID of services
        :param api_version: Service version.
        :param session: Keystone session
        :param engine: Type of operation ['HEAT', 'DIRECT']
        """
        super(BaseManager, self).__init__()
        self.name_or_id = name_or_id
        self.api_version = api_version
        self.session = session
        self.endpoint = endpoint
        self.engine = engine.lower()
        self.kwargs = kwargs

    def refresh(self, session):
        """Refresh connection
        Subclass should be override this class
        :param session: Keystone session

        :return:
        """
        self.session = session

    def convert_into_with_meta(self, raw):
        """Convert raw data to munch
        :param raw:
        :return:
        """

    @property
    def supported(self):
        return True

    @property
    def supported_heat(self):
        """Allow to do action by deploying heat stack
        Subclass should be override this method

        :return:
        """
        return True

    @property
    def supported_console(self):
        """Allow to do action by making http requests directly to openstack services
        Subclass should be override this method

        :return:
        """
        return True

    @property
    def resource_name(self):
        return self.resource_class.__name__


class Resource(object):
    """Base class for FoxCloud resources.
    This is pretty much just a bag for attributes.
    """
    HUMAN_ID = False
    NAME_ATTR = 'name'
    DEFAULT_SORT_BY = ['create_date__desc']

    def __init__(self, manager, info, loaded=True):
        """Populate and bind to a manager

        :param manager: BaseManager
        :param info: dictionary representing resource attributes
        :param loaded: prevent lazy-loading if set to True
        """
        self.manager = manager
        self._info = info
        # self.data = None
        # self.add_details(info)
        self._loaded = loaded

    @property
    def human_id(self):
        """Human-readable ID which can be used for bash completion. """
        if self.HUMAN_ID:
            name = getattr(self, self.NAME_ATTR, None)
            if name is not None:
                return strutils.to_slug(name)
        return None

    def get(self):
        """Support for lazy loading details.
        """
        self.set_loaded(True)
        if not hasattr(self.manager, 'get'):
            return

    def __getattr__(self, k):
        if k not in self.__dict__:
            # NOTE(bcwaldon): disallow lazy-loading if already loaded once
            if not self.is_loaded():
                self.get()
                return self.__getattr__(k)

            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def __eq__(self, other):
        if not isinstance(other, Resource):
            return NotImplemented
        # two resources of different types are not equal
        if not isinstance(other, self.__class__):
            return False
        return self._info == other._info

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val

    # def to_dict(self):
    #     return copy.deepcopy(self._info)

    def ok(self, data):
        return None, data

    def fail(self, error):
        return error, None

    def parse_ctx_listing(self, data):
        """
        Parse listing info.
        :param data:
        :return:
        """
        page = int(data.get('page') or 1)
        page_size = int(data.get('page_size') or 1000)
        sort_by = data.get('sort_by')
        fields = data.get('fields') or None
        extra_fields = data.get('extra_fields') or None

        sort_bys = []
        if isinstance(sort_by, str):
            sort_by = sort_by.split(',')
            for item in sort_by:
                item = item.split('__')
                attr = item[0]
                direction = item[1] if len(item) == 2 else 'asc'
                sort_bys.append((attr, direction))

        return {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_bys or None,
            'fields': fields,
            'extra_fields': extra_fields,
        }

    def parse(self, fields=None, extra_fields=None, extra_field_getter=None, **paging):
        if isinstance(self._info, list):
            objects = [self._to_dict(obj) for obj in self._info]
            if 'page_size' in paging:
                page_data = self._paginate(objects, **paging)
                objects = page_data['data']
            else:
                page_data = None

            objects_ = []
            for o in objects:
                err, item = self._parse_i(o, fields=fields, extra_fields=extra_fields,
                                          extra_field_getter=extra_field_getter)
                if err:
                    return self.fail(err)
                objects_.append(item)

            if page_data:
                page_data['data'] = objects_
                return None, page_data
            else:
                return None, objects_

        return self._parse_i(self._info, fields=fields, extra_fields=extra_fields,
                             extra_field_getter=extra_field_getter)

    def _to_dict(self, obj):
        """
        Convert obj to dict.
        :param obj:
        :return:
        """
        if not obj:
            return obj

        if isinstance(obj, dict):
            return obj
        else:
            obj_dict = None
            if isinstance(obj, munch.Munch):
                obj_dict = obj.toDict()
            else:
                to_dict = getattr(obj, 'to_dict', None)
                if to_dict:  # TODO: Check type if function
                    obj_dict = obj.to_dict()

            return obj_dict if obj_dict is not None else obj

    def _parse_i(self, obj, fields=None, extra_fields=None, extra_field_getter=None):
        obj_dict = self._to_dict(obj)
        if not obj_dict:
            return None, obj

        ret = obj_dict
        if extra_fields and extra_field_getter:
            for f in extra_fields:
                err, data = extra_field_getter(obj_dict, f)
                if err:
                    return self.fail(err)
                ret[f] = data

        if fields:
            if extra_fields:
                fields = fields + extra_fields
            ret = self._filter_fields(ret, fields)

        return None, ret

    def _paginate(self, objects, page, page_size, sort_by=None, **kw):
        """
        Paginate data.
        :param objects:
        :param page:
        :param page_size:
        :param sort_by:
        :return:
        """
        # Python sorted is stable sort, so we can call it multiple times
        # to sort by multiple fields. Performance may be an issue.
        # See: https://stackoverflow.com/questions/5212870/sorting-a-python-list-by-two-fields

        if page_size is None:
            return objects

        if sort_by is None:
            sort_by = self.DEFAULT_SORT_BY

        for sort in sort_by:
            reverse = sort[1] == 'desc'
            objects = sorted(objects, key=lambda x: x.get(sort[0], 0), reverse=reverse)

        count = len(objects)
        page = page or 1
        start = min((page - 1) * page_size, count)
        end = min(start + page_size, count)
        data = objects[start:end] if start < end else []
        return {
            'data': data,
            'has_more': end < count,
            'next_page': page + 1 if end < count else None,
            'prev_page': page - 1 if page > 1 else None,
        }

    def _filter_fields(self, objects, fields):
        """
        Filter fields for objects.
        :param objects:
        :param fields:
        :return:
        """
        if fields is None:
            return objects

        if isinstance(objects, dict):
            result = {}
            for f in fields:
                result[f] = objects.get(f)
        else:
            result = []
            for obj in objects:
                obj_data = {}
                for f in fields:
                    obj_data[f] = obj.get(f)
                result.append(obj_data)

        return result
