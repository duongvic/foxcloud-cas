#
# Copyright (c) 2020 FTI-CAS
#

from __future__ import absolute_import


class Object(object):
    """
    Base class for classes in the logical model
    Contains common attributes and methods
    """

    def __init__(self, name, context):
        self.name = name
        self._context = context
        self.flags = None
        # stack identities
        self.stack_name = None
        self.stack_id = None

    @property
    def dn(self):
        """
        Returns distinguished name for object
        """
        return self.name + "." + self._context.name
