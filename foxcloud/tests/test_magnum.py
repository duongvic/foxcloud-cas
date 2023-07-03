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


def test_cluster_template():
    """
    :return:
    """
    cs = client.Client('1', engine='console', services='coe', **params)
    labels = {
        'kube_dashboard_enabled': True,
    }
    uuid = '5fda2bf7-cf01-4b7b-aecd-c8b7e0a49c59'
    # data = cs.coe.create_cluster_template(name='test_khanhct', keypair_id='khanhct17', docker_volume_size=10,
    #                                       external_network_id='761e7cf6-fb7e-4555-8862-9c777c0b3145',
    #                                       image_id='4121d7f4-5eb8-48b1-9854-a952d9a893a7', labels=labels)
    # data = cs.coe.get_cluster_templates()
    # name, template_id, keypair_id, node_flavor_id, master_flavor_id,
    # node_count = 1, master_count = 1, network_id = None, subnet_id = None, timeout = 60,
    # floating_ip_enabled = True, labels = {}):
    # data = cs.coe.create_cluster(name='khanhct', template_id=uuid, keypair_id='khanhct17',
    #                              node_flavor_id='818a1286-a729-477c-9d6a-cf792e26cf40',
    #                              master_flavor_id='818a1286-a729-477c-9d6a-cf792e26cf40',
    #                              node_count=1, master_count=1, subnet_id='99096ad1-5a08-4c3e-84ee-f9b1374a5c22',
    #                              timeout=60, floating_ip_enabled=True, labels={}, force=False)
    a = [
        {
            "path": "/master_lb_enabled",
            "value": "True",
            "op": "replace"
        }
    ]
    data = cs.coe.update_cluster_template(template_id='cd6b30ad-64b6-4957-a187-c3cb48249d9f', patch=a)
    print(data.parse())


def c(**kwargs):
    print(kwargs['name'])


def test_cluster():
    """

    :return:
    """
    cs = client.Client('1', engine='console', services='coe', **params)


test_cluster_template()
