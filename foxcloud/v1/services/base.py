#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import base


class BaseChildManager(base.BaseManager):
    """Manager for API services.
    Managers interact with a particular type of API (Neutron, Nova, Cinder, Octavia,..)
    and provide operations for them.
    """

