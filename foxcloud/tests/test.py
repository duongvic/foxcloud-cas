import os
import uuid

from keystoneauth1 import loading
from keystoneauth1 import session

from troveclient import client


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


def create_cluster(name, datastore_id, datastore_version_id, flavor_id, volume_size,
                   volume_type=None, number_of_instances=3, network_id=None, locality=None,
                   availability_zone=None, extended_properties=None, configuration=None):
    os_cloud_config = {
        'verify': False,
        'region_name': 'regionOne',
        'auth': {
            'username': 'tester',
            'password': 'tester',
            'project_name': 'tester',
            'auth_url': 'https://example.com:13000/v3',
            'project_domain_name': 'Default',
            'user_domain_name': 'Default',
        }
    }

    sess = get_session(os_cloud_config)
    trove_client = client.Client(version='1', session=sess)
    instances = []
    for i in range(0, number_of_instances):
        instance = {
            'name':  '{}-member-{}'.format(name, 'member', str(i + 1)),
            'flavorRef': flavor_id,
            'volume': {
                'size': volume_size,
            },
            'net-id': network_id,
        }
        if volume_type:
            instance['volume']['type'] = volume_type
        if availability_zone:
            instance['availability_zone'] = availability_zone
        instances.append(instance)

    trove_client.clusters.create(name, datastore_id, datastore_version_id, instances,
                                 locality, extended_properties, configuration)


# create_cluster(name='test1', datastore_id='16e745f6-f5d3-4876-9207-2486352d537f',
#                datastore_version_id='4d9cb75f-fe87-4152-bf04-3f4e72f22bc7',
#                flavor_id='ba45e5dc-3f7f-4de1-863c-109c09e6415d', volume_size=10,
#                volume_type=None, number_of_instances=3, network_id='761e7cf6-fb7e-4555-8862-9c777c0b3145',
#                locality=None, availability_zone=None, extended_properties=None, configuration=None)




def test_cluster():
    """
    :return:
    """
    cs = client.Client('1', engine='console', services='trove', **params)
    # data = cs.trove.get_datastores().data
    # data = cs.trove.get_datastore_versions('9192fb0e-7ece-4dd7-a2f2-be8bbed4ad1a').data

    data = cs.trove.create_cluster(name='test1', datastore_id='16e745f6-f5d3-4876-9207-2486352d537f',
                                  datastore_version_id='4d9cb75f-fe87-4152-bf04-3f4e72f22bc7',
                                  flavor_id='ba45e5dc-3f7f-4de1-863c-109c09e6415d', volume_size=10,
                                  volume_type=None, number_of_instances=3, network_id='761e7cf6-fb7e-4555-8862-9c777c0b3145',
                                  locality=None, availability_zone=None, extended_properties=None, configuration=None)
    data = cs.trove.delete_cluster('b1b99a8d-0b4f-489e-a7d3-3a9eb3c2a83e')
    print(data)


def test_create_instance():
    os_cloud_config = {
        'verify': False,
        'region_name': 'regionOne',
        'auth': {
            'username': 'tester',
            'password': 'tester',
            'project_name': 'tester',
            'auth_url': 'https://example.com:13000/v3',
            'project_domain_name': 'Default',
            'user_domain_name': 'Default',
        }
    }

    sess = get_session(os_cloud_config)
    trove_client = client.Client(version='1', session=sess)
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
    trove_client.instances.create(name='test2', flavor_id='ba45e5dc-3f7f-4de1-863c-109c09e6415d',
                                  volume=volume, databases=databases, users=users, nics=nics,
                                  datastore_version_id='4d9cb75f-fe87-4152-bf04-3f4e72f22bc7',
                                  datastore_id='16e745f6-f5d3-4876-9207-2486352d537f')


from collections import OrderedDict
a = OrderedDict('name')
print(a)
