import os
import uuid

from keystoneauth1 import loading
from keystoneauth1 import session

from foxcloud import client


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


os_cloud_config = {
    'verify': False,
    'region_name': 'regionOne',
    'auth': {
        'username': 'khanhct',
        'password': 'khanhct',
        'project_name': 'khanhct',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
        'project_domain_name': 'Default',
        'user_domain_name': 'Default',
    }
}
session_ = get_session(os_cloud_config)
params = {
    'os_auth': os_cloud_config['auth'],
}

attrs = {
    'stack': {
        'name': 'octavia',
        'file': 'pod.yaml',
        'task_id': uuid.uuid4().hex,
        'flags': {
            'no_setup': False,
            'no_teardown': False,
            'os_cloud_config': {
                'verify': False,
                'region_name': 'regionOne',
                'auth': {
                    'username': 'admin',
                    'password': 'sYHWJGY37CDoLd15jgC3s4Hzr',
                    'project_name': 'admin',
                    'auth_url': 'https://hn.foxcloud.vn:13000/v3',
                    'project_domain_name': 'Default',
                    'user_domain_name': 'Default',
                }
            }
        },
    },
    'resources': {
        'lb': {
            'vip_subnet': '096a001d-ebd0-418a-adf0-cf55679fe51b'
        },
        # pool, delay, max_entries, timeout, type
        'pool_monitor': {
            'delay': 5,
            'max_entries': 5,
            'timeout': 5,
            'type': 'HTTP',
            'url_path': "/",
        },
        'pool_members': [
            {
                'address': '42.112.37.246',
                'port': 80,
                'weight': 1
            }
        ],
        'pool': {
            'alg': 'ROUND_ROBIN',
            'protocol': 'HTTP',
        },
        'listener': {
            'protocol': 'HTTP',
            'port': 80,
        }
    }
}


def test_heat():
    """

    :return:
    """
    cs = client.Client('1', engine='console', services='lbaas', **params)
    print(cs.lbaas.create_allinone(attrs))


a = {
    "l7policy_id": "5fb64b9f-e8b9-41e0-ab81-4a80e59e44e0",
    "compare_type": "REGEX",
    "invert": False,
    "type": "PATH",
    "value": "/images*",
    "tags": ["test_tag"]
}

def test_console():
    """

    :return:
    """
    cs = client.Client('1', engine='console', services='lbaas', **params)
    # print(cs.lbaas.delete_lb('e5d884bc-4567-4ead-ad25-cc26cb3053bd').parse())
    print(cs.lbaas.create_l7rule(**a).parse())
    # print(cs.lbaas.create_allinone(attrs['resources']))


# test_console()
import re
# from foxcloud.v1.utils import hash_util
#
# pri, pub = hash_util.gen_ssh_key()

# #format = '^[ssh-rsa AAAA].[0-9A-Za-z+/]+[=]{0,3} ([^@]+@[^@]+)'
#
x = re.search("https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
              "http://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url")
# # x = re.search('^[a-z]{8,}([a-z0-9_])$', "dsdsadadsadsadsadsadgfddfgfdg")
# # #'^[a-z]{8,}([a-z0-9_])$',error='Must be greater than 8 characters'
# # x = re.search(a, "192.192.192.2/23")
print(x)
# # 'subnet_id': fields.Str(required=True,
# #                         validate=validate.Regexp('((\d){1,3}\.){3}(\d){1,3}\/(\d){1,3}')),
# # 'vip_address': fields.Str(required=False,
# #                           validate=validate.Regexp('((\d){1,3}\.){3}((\d){1,3})$')),