#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud.v1.utils import sys_util
from foxcloud.v1.services.stack.orchestrator import heat


class Flags(object):
    """Class to represent the status of the flags in a context"""

    _FLAGS = {
        'no_setup': False,
        'no_teardown': False,
    }

    def __init__(self, **kwargs):
        for name, value in self._FLAGS.items():
            setattr(self, name, value)

        for name, value in ((name, value) for (name, value) in kwargs.items()
                            if name in self._FLAGS):
            setattr(self, name, value)

    def parse(self, **kwargs):
        """Read in values matching the flags stored in this object

        :param kwargs
        :return
        """
        if not kwargs:
            return

        for name, value in ((name, value) for (name, value) in kwargs.items()
                            if name in self._FLAGS):
            setattr(self, name, value)


class Context(object):
    """Class that represents a context in the logical model"""
    list = []
    SHORT_TASK_ID_LEN = 8

    def __init__(self, session):
        # Context.list.append(self)
        self._flags = Flags()
        self._name = None
        self._task_id = None
        self.file_path = None
        self._name_task_id = None
        self._session = session

    def init(self, attrs):
        """Initiate context

        :param attrs:
        :return:
        """
        self._name = attrs['name']
        self._task_id = attrs['task_id']
        self._flags.parse(**attrs.get('flags', {}))
        self._name_task_id = '{}-{}'.format(self._name, self._task_id[:self.SHORT_TASK_ID_LEN])

    @property
    def name(self):
        if self._flags.no_setup or self._flags.no_teardown:
            return self._name
        else:
            return self._name_task_id

    @property
    def task_id(self):
        return self._task_id

    @property
    def assigned_name(self):
        return self._name

    @staticmethod
    def get_cls(context_type):
        """Return class of specified type.

        :param context_type:
        :return:
        """
        for context in sys_util.itersubclasses(Context):
            if context_type == context.__context_type__:
                return context
        raise RuntimeError("No such context_type %s" % context_type)

    def _create_new_stack(self, heat_template, block=True, timeout=10):
        """
        Create a new heat stack
        :param heat_template:
        :param block
        :param timeout
        :return:
        """
        return heat_template.create(block=block, timeout=timeout)

    def _update_new_stack(self, heat_template, block=True, timeout=10):
        """
        Update a new heat stack
        :param heat_template:
        :param block
        :param timeout
        :return:
        """
        return heat_template.update(block=block, timeout=timeout)

    def _retrieve_existing_stack(self, stack_name):
        if not self._session:
            return None

        stack = heat.HeatStack(name_or_id=stack_name, session=self._session)
        if stack.get():
            return stack
        else:
            return None

    def build_output(self):
        """
        Build output
        Subclass should be override this method
        :return:
        """

    def get(self):
        """
        Subclass should override this method.
        :return:
        """

    def create(self):
        """
        Subclass should override this method.
        :return:
        """

    def update(self):
        """
        Subclass should override this method.
        :return:
        """

    def delete(self):
        """
        Subclass should override this method.
        :return:
        """

    def abandon(self):
        """
        Subclass should override this method.
        :return:
        """


