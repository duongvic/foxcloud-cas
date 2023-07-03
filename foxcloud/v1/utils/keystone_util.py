#
# Copyright (c) 2020 FTI-CAS
#

import os

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient.v3 import client

def get_credentials(os_info):
    """
    Returns a creds dictionary filled with parsed from env
    Keystone API version used is 3;
    environment variable 'OS_TENANT_NAME' is replaced by
    'OS_PROJECT_NAME'.
    """
    credentials = os_info['auth']

    if not credentials:

        credentials = {
            'username': os.environ.get('OS_USERNAME'),
            'password': os.environ.get('OS_PASSWORD'),
            'auth_url': os.environ.get('OS_AUTH_URL'),
            'project_name': os.environ.get('OS_PROJECT_NAME'),
        }
        if os.getenv('OS_USER_DOMAIN_NAME'):
            credentials['user_domain_name'] = os.getenv('OS_USER_DOMAIN_NAME')

        if os.getenv('OS_PROJECT_DOMAIN_NAME'):
            credentials['project_domain_name'] = os.getenv('OS_PROJECT_DOMAIN_NAME')

    return credentials


def get_session_auth(os_info):
    """
    Get authentication session
    :return:
    """
    loader = loading.get_plugin_loader('password')
    creds = get_credentials(os_info)
    auth = loader.load_from_options(**creds)
    return auth


def get_session(os_info):
    """
    Get s new session
    :return:
    """
    auth = get_session_auth(os_info)
    try:
        cacert = os.environ['OS_CACERT']
    except KeyError:
        return session.Session(auth=auth)
    else:
        insecure = os.getenv('OS_INSECURE', '').lower() == 'true'
        cacert = False if insecure else cacert
        return session.Session(auth=auth, verify=cacert)


def get_endpoint(os_info, service_type, endpoint_type='publicURL'):
    """
    Get s new session
    :param os_info
    :param service_type
    :param endpoint_type
    :return:
    """
    auth = get_session_auth(os_info)
    # for multi-region, we need to specify region
    # when finding the endpoint
    session_ = get_session(os_info)
    return session_.get_endpoint(auth=auth, service_type=service_type,
                                 endpoint_type=endpoint_type,
                                 region_name=os_info['region_name'])


def get_keystone_client(os_info):
    """
    Get Keystone client

    :param os_info
    :return:
    """
    sess = get_session(os_info)
    return client.Client(session=sess)
