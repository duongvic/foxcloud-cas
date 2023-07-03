#
# Copyright (c) 2020 FTI-CAS
#


from foxcloud.v1.services.ceph.base import BaseCeph


class Console(BaseCeph):
    __engine_type__ = 'console'
