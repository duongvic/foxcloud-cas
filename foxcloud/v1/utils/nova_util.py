#
# Copyright (c) 2020 FTI-CAS
#

import logging
import os

from novaclient import client as nova_client
from novaclient import exceptions as nova_exc


def get_nova_client(version, session):
    """
    Get nova client
    :param version:
    :param session:
    :return:
    """
    return nova_client.Client(version, session=session)


def get_server(client, server_id):
    """
    Get server
    :param client:
    :param server_id:
    :return:
    """
    try:
        servers = client.servers.get(server=server_id)
        return servers
    except nova_exc.ClientException:
        return None


