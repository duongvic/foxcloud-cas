#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud.v1.services.s3.base import BaseStorage


class Heat(BaseStorage):
    """

    """
    __engine_type = 'heat'

    def __init__(self, session):
        super().__init__(session)
