#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud.v1.services.ceph.base import BaseCeph


class Heat(BaseCeph):
    __engine_type__ = 'heat'
