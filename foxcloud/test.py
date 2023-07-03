from foxcloud.v1.services.stack.orchestrator import heat
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
        'username': 'khanhct',
        'password': 'khanhct',
        'project_name': 'khanhct',
        'auth_url': 'https://hn.foxcloud.vn:13000/v3',
        'project_domain_name': 'Default',
        'user_domain_name': 'Default',
    }
}

sess = get_session(os_cloud_config)
# stack = heat.HeatStack(name_or_id='fb6c81ed-1f49-48e9-b746-dd2e4f6efe19', session=session)
# print(stack)

# from foxcloud.v1.utils import sys_util
# from foxcloud.v1.services.shade import base
#
# a = sys_util.find_subclasses('heat', base.BaseInstance)

# from novaclient import client
#
# shade = client.Client(version='2', session=session)
# flavor = shade.flavors.get('2f5852a7-b569-4814-bd08-95eea6cbac3b')
# print(flavor)
# info = stack.create(template={}, heat_parameters={}, wait=True, timeout=120, rollback=True)
# print(info)
from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud import base


from foxcloud import client




# https://172.16.1.56:6443/  cn=admin,dc=ldap,dc=foxcloud,dc=vn / Cas@2020 thông in con đây anh @Khanh ạ
import pprint,ldap,ldap.modlist


#   'who': dn,
#   'cred': 'Cas@2020',
#   'filterstr': '(objectClass=*)',
#   'scope': ldap.SCOPE_BASE
# })
#
# ldap.trace_level = 2
#
# l = ldap.ldapobject.ReconnectLDAPObject(
#     ldap_url.initializeUrl(),
#     trace_level=ldap.trace_level,
# )
# l.protocol_version = ldap.VERSION3
# who = ldap_url.who
# cred = ldap_url.cred

# objectClass: account
# objectClass: inetOrgPerson
# objectClass: inetUser
# objectClass: ldapPublicKey
# objectClass: ntUser
# objectClass: organizationalPerson
# objectClass: person
# objectClass: posixaccount
# objectClass: top
# ldap_uri = "ldap://172.16.1.56"
# password = 'Cas@2020'
# dn='cn=admin,dc=ldap,dc=foxcloud,dc=vn'
# dn1='cn=khanhct,ou=users,dc=ldap,dc=foxcloud,dc=vn'
# l = ldap.initialize(ldap_uri,trace_level=0)
# l.simple_bind_s(dn, password)
# print(l.delete(dn1))
# new_test_dn = "cn=khanhct,ou=Users,dc=ldap,dc=foxcloud,dc=vn"
# new_test_entry = {
#     'objectClass': ['account'.encode('utf-8'), 'posixAccount'.encode('utf-8')],
#     'uid':['khanhct'.encode('utf-8')],
#     'cn':['KhanhCT'.encode('utf-8')],
#     'uidNumber':['10000'.encode('utf-8')],
#     'gidNumber':['10000'.encode('utf-8')],
#     'homeDirectory':['/home/users/khanhct'.encode('utf-8')],
#     'userPassword':['khanhct'.encode('utf-8')],
# }

# new_person_entry = {
#     'objectClass': ['person'.encode('utf-8'), 'top'.encode('utf-8')],
#     'cn':['khanhct3'.encode('utf-8')],
#     'sn':['khanhct3'.encode('utf-8')],
#     'userPassword':['khanhct'.encode('utf-8')],
# }
#
# msg_id = l.add(
#   new_test_dn,
#   ldap.modlist.addModlist(new_person_entry),
# )
# a, b = l.result(msg_id)
# print(a)
# print(b)
# l.unbind()

# msgid = l.search('ou=Users', ldap.SCOPE_SUBTREE,'(cn=demo_admin)')
# # new_dn = 'ou=Users,uid=khanhct'
# # l.delete(dn=new_dn)
# print(msgid)
# while 1:
#   l.search_s(ldap_url.dn,ldap_url.scope,ldap_url.filterstr,ldap_url.attrs)
#   sys.stdin.readline()
#
# print(client.list_services(version=1))
# cs = client.Client('1', sess, engine='console', **params)
# print(cs.ceph.rollback_snapshot('07bb2bc1-b753-4672-9192-8e809129b056',
#                                 '97bb2bc1-b753-4672-9192-8e809129b056'))
# cs.shutdown()

#lb
# a = cs.lbaas.create_lb(name='kkskksksksks', subnet_id='99096ad1-5a08-4c3e-84ee-f9b1374a5c22', provider='octavia', description="kkskksksksks")
# a = cs.lbaas.list_lbs()

# listener
# listener = {
#     'name': "listener",
#     'description': 'description',
#     'protocol': 'HTTPS',
#     'port': 80,
#     'lb_id': 'bdaaa4c3-4cf9-44bf-ad50-82734b2219fa',
# }
# listener_id = '4915b3f8-ed96-4e7e-8a48-4f31f79ec3ab'
# lb_id = 'bdaaa4c3-4cf9-44bf-ad50-82734b2219fa'
# pool_id = '3f30b4d2-d0b9-443d-a2bc-52c2e700a256'
# member_id = '15868c9d-df74-44f9-b63d-10c02c778bad'
# {'healthmonitor': {'id': '1d87025d-b7bc-4cc9-bb04-894446bd51d5'
# {'l7policy': {'id': '3f53802d-69be-461c-921b-2ce3451eadea'
# a = cs.lbaas.create_pool(name="pool", description='description', listener_id=listener_id,
#                          protocol='HTTPS')
# data = self.api.add_member(pool_id, address, port, name,
#                                    is_backup, subnet_id, weight, **kwargs)
# a = cs.lbaas.add_member(pool_id=pool_id, address='172.22.0.65', port=80, name='test')
# a = cs.lbaas.create_monitor(pool_id, 10, 10, 'HTTP', name='monitor',
#                        http_method='GET', max_retries=10, max_retries_down=10,
#                        url_path='/')
# a = cs.lbaas.create_l7policiy('REJECT', listener_id, name=None, description='create_l7policiy', position=None)

# from foxcloud.v1.utils import sys_util
#
# sys_util.find_subclasses("", base_class=Foo)
# engine = '10'
# msg = _("Not supported engine '%s'. "
#                 "Expected %s") % (engine ,' or '.join(e.upper() for e in base.SUPPORTED_ENGINES))
# print(msg)