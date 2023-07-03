import ipaddress

from neutronclient.common import exceptions as neu_exc
from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.shade.base import BaseShade


class Console(BaseShade):
    __engine_type__ = 'console'

    def __init__(self, session):
        super().__init__(session)

    def create_server(self, info):
        """
        Subclass should be override this method
        :param info:
        :return:
        """

    def update_server(self, info):
        """
        Subclass should be override this method
        :param info:
        :return:
        """

    def delete_server(self, server_id):
        """
        Subclass should be override this method
        :param server_id:
        :return:
        """