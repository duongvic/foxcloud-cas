from foxcloud import client
import os

from keystoneauth1 import loading
from keystoneauth1 import session


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
        'username': 'u1',
        'password': '123',
        'project_name': 'u1',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
        'project_domain_name': 'tripleodomain',
        'user_domain_name': 'tripleodomain',
    }
}
session_ = get_session(os_cloud_config)
params = {
    'os_auth': os_cloud_config['auth'],
}

pgs = {'pgrp1': {'policy': 'availability'}}
sgs = {'servergroup1': {'policy': 'affinity'}}

networks = [
    {
        'name': 'k8s-mgmt-net',
        "subnet": 'k8s-mgmt-subnet',
        'net_flags': {
            'is_existing': True
        }
    }
]

servers = [
    {
        'name': 'VM1',
        'floating_ip': False,
        'flavor': 'm1.small',
        'image': 'Ubuntu16.04',
        'server_group': None,
        'username': 'khanhct',
        'password': 'Cas@2020',
        'instances': 1,
        'volumes': [
            {
                'size': 10,  # Unit GB
                'is_boot': True,
                # 'mountpoint': '/dev/vdb',
                'read_only': False,
                'snapshot_id': None,
                'image': 'Ubuntu16.04',
                'vol_flags': {
                    "is_existing": False,
                }
            },
            {
                'size': 10,  # Unit GB
                # 'mount_point': '/dev/vdb',
                'is_boot': False,
                'read_only': False,
                'vol_flags': {
                    "is_existing": False,
                }
            },
        ]
    }
]

from foxcloud.v1.utils import hash_util
import uuid
pri, pub = hash_util.gen_ssh_key()
uuid2222 = uuid.uuid4().hex
keypair = {
    'name': uuid2222[:-8],
    'public_key': pub,
    'key_type': 'ssh',
    'key_flags': {
        'is_existing': False
    }
}

attrs = {
    'stack': {
        'name': 'khanhct',
        'task_id': uuid2222[:-8],
        'flags': {
            'no_setup': False,
            'no_teardown': False,
        },
    },
    'resources': {
        'placement_groups': {},
        'server_groups': {},
        'networks': networks,
        'keypair': keypair,
        'servers': servers,
        "security_group": {
            "name": "sg1",
            "description": "description",
            "rules": [
                {
                    "direction": "ingress",
                    "protocol": "tcp",
                    'ether_type': 'IPv4',
                    "port_range": "80:80",
                    "source": "0.0.0.0",
                    "description": "https",
                    'remote_ip_prefix': '0.0.0.0/0',
                }
            ]
        }
    }
}

def test_volume():
    """

    :return:
    """
    cs = client.Client('1', engine='console', services='shade', **params)
    data = cs.shade.add_router_interface('52b836f2-0cd0-477d-9243-931b29fa29f7', '627f95bb-b9dc-44ad-ae82-f056f4aea03b',
                                         '73505a41-556a-451e-8be5-c9e936108665')
    print(data)


def test_network():
    cs = client.Client('1', engine='console', services='shade', **params)
    # data = cs.shade.create_neutron_network(name='test2', shared=True, admin_state_up=True,
    #                                        external=False, provider=None, project_id=None,
    #                                        availability_zone_hints=None,
    #                                        port_security_enabled=None,
    #                                        mtu_size=None)
    listing = {
            'page': 1,
            'page_size': 20,
            'sort_by':  None,
            'fields': None,
            'extra_fields': None,
        }
    # router:external: True
    'aaf3073a-72c5-449e-ab82-8bc8568f865d'
    filters = {
        'network_id': '22d9e8a7-1e4e-4420-b78e-dc8b5c4b20c6fdfsffdfd',
        'enable_dhcp': False
    }
    data = cs.shade.get_neutron_subnet('006b87d9-cb9f-4e56-9c73-97c5a67b05eb')
    t = data.parse(**listing)
    print(t)


def test_keypair():
    from foxcloud.v1.utils import hash_util
    cs = client.Client('1', engine='console', services='shade', **params)
    # pri, pub = hash_util.gen_ssh_key()
    # print(pub)
    # data = cs.shade.create_keypair(name='test_keypair', public_key=pub)
    listing = {
        'page': 1,
        'page_size': 20,
        'sort_by': None,
        'fields': None,
        'extra_fields': None,
    }
    data = cs.shade.get_keypair('khanhct11111')
    print(data.parse())


def test_server():
    """

    :return:
    """
    cs = client.Client('1', engine='heat', services='shade', **params)
    print(cs.shade.get_volume_backups(search_opts={'volume_id': '5366d95a-ec59-435f-8f37-038176d43f55'}))


test_server()
