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
    'keystone_session': session_,
}


# from troveclient import client
# trove_client = client.Client(version='1.0', session=session)
# # print(trove_client.datastores.list())

def test_cluster():
    """
    :return:
    """
    params = {
        'os_auth': os_cloud_config['auth'],
    }

    cs = client.Client('1', engine='console', services='trove', **params)
    print(cs.trove.get_datastore_version(datastore_id='', datastore_version_id='').parse())
    # data = cs.trove.get_datastores().data
    # data = cs.trove.get_datastore_versions('9192fb0e-7ece-4dd7-a2f2-be8bbed4ad1a').data

    # data = cs.trove.create_cluster(name='test1', datastore_id='16e745f6-f5d3-4876-9207-2486352d537f',
    #                               datastore_version_id='4d9cb75f-fe87-4152-bf04-3f4e72f22bc7',
    #                               flavor_id='ba45e5dc-3f7f-4de1-863c-109c09e6415d', volume_size=10,
    #                               volume_type=None, number_of_instances=3, network_id='761e7cf6-fb7e-4555-8862-9c777c0b3145',
    #                               locality=None, availability_zone=None, extended_properties=None, configuration=None)
    # data = cs.trove.delete_cluster('b1b99a8d-0b4f-489e-a7d3-3a9eb3c2a83e')
    # print(data)


def test_instance():
    cs = client.Client('1', engine='console', services='trove', **params)
    databases = [
        {
            "character_set": "utf8",
            "collate": "utf8_general_ci",
            "name": "sampledb0"
        },
        {
            "character_set": "utf8",
            "collate": "utf8_general_ci",
            "name": "sampledb1"
        }
    ]
    users = [
        {
            'name': 'admin',
            'password': 'admin',
            "databases": [
                {
                 'name': 'sampledb1'
                }
            ],
        }
    ]
    volume = {
        'size': 10,
        # 'type': None
    }
    nics = [
        {
         'net-id': '761e7cf6-fb7e-4555-8862-9c777c0b3145'
        }
    ]
    # mysql -h 172.22.3.214 -u 'u1' -p
    data = cs.trove.create_instance(name='test2', flavor_id='ba45e5dc-3f7f-4de1-863c-109c09e6415d',
                                    volume=volume, databases=None, users=None, nics=nics,
                                    datastore_version_id='4d9cb75f-fe87-4152-bf04-3f4e72f22bc7',
                                    datastore_id='16e745f6-f5d3-4876-9207-2486352d537f',
                                    replica_of='c916843c-f1e8-426e-b39f-87dc0d324821',
                                    replica_count=2, wait=True)
    # data = cs.trove.get_instance('c916843c-f1e8-426e-b39f-87dc0d324821').data
    # data = cs.trove.do_instance_action('c916843c-f1e8-426e-b39f-87dc0d324821', 'restart')
    data = cs.trove.create_backup(name="11111", instance_id='c916843c-f1e8-426e-b39f-87dc0d324821')
    print(data)


test_cluster()