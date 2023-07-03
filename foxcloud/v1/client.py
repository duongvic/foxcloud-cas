import os
from urllib.parse import urlparse

from keystoneauth1 import loading
from keystoneauth1 import session as ks_session
from foxcloud import exceptions as fox_exc
from foxcloud.i18n import _
from foxcloud.v1.services.shade import client as shade_client
from foxcloud.v1.services.lbaas import client as lb_client
from foxcloud.v1.services.trove import client as trove_client
from foxcloud.v1.services.s3 import client as storage_client
from foxcloud.v1.services.ceph import client as ceph_client
from foxcloud.v1.services.coe import client as coe_client
from foxcloud.v1.services.ldap import client as ldap_client

SERVICES = ['ceph', 'coe', 'lbaas', 's3', 'trove', 'shade', 'ldap']


def get_session_auth(os_creds):
    """
    Get authentication session
    :param os_info
    :return:
    """
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(**os_creds)
    return auth


def get_session(os_creds):
    """
    Get s new session
    :param os_creds
    :return:
    """
    auth = get_session_auth(os_creds)
    try:
        cacert = os.environ['OS_CACERT']
    except KeyError:
        return ks_session.Session(auth=auth)
    else:
        insecure = os.getenv('OS_INSECURE', '').lower() == 'true'
        cacert = False if insecure else cacert
        return ks_session.Session(auth=auth, verify=cacert)


class Client(object):
    DEFAULT_ENDPOINTS = {}

    def __init__(self, api_version='1', engine='HEAT', services=None, **kwargs):
        """Initialize FoxCloud client object

        :param api_version: FoxCloud version
        :param session: Keystone Session
        :param engine: Supported two engines ['heat', 'console']
        :param services:
        :param kwargs:
        """
        self._api_version = api_version
        os_auth = kwargs.get('os_auth') or {}
        self.set_default_endpoints(auth_url=os_auth.get('auth_url'))
        if services is None:
            services = SERVICES

        for service in services:
            func_call = getattr(self, 'init_{}'.format(service))
            func_call(service, api_version, engine, **kwargs)

    def init_ceph(self, name, api_version, engine, **kwargs):
        ceph_config = kwargs.get('ceph_config')
        ceph_pool = kwargs.get('ceph_pool')
        ceph_keyring = kwargs.get('ceph_keyring')
        session = None
        self.ceph = ceph_client.CephManager(name, api_version, session,
                                            engine, config_file=ceph_config,
                                            keyring=ceph_keyring,
                                            pool=ceph_pool)

    def init_coe(self, name, api_version, engine, **kwargs):
        endpoint = kwargs.get('magnum_endpoint')
        if not endpoint:
            endpoint = self.DEFAULT_ENDPOINTS['magnum']

        os_auth = kwargs.get('os_auth')
        if not isinstance(os_auth, dict):
            msg = _("The os_auth of '%s' services must be a list object") % engine
            raise fox_exc.FoxCloudException(msg)
        session = get_session(os_auth)

        self.coe = coe_client.COEManager(name, api_version, session,
                                         engine, endpoint)

    def init_lbaas(self, name, api_version, engine, **kwargs):
        endpoint = kwargs.get('lb_endpoint')
        if not endpoint:
            endpoint = self.DEFAULT_ENDPOINTS['lbaas']

        os_auth = kwargs.get('os_auth')
        if not isinstance(os_auth, dict):
            msg = _("The os_auth of '%s' services must be a list object") % engine
            raise fox_exc.FoxCloudException(msg)
        session = get_session(os_auth)

        self.lbaas = lb_client.LbaasManager(name, api_version,
                                            session, engine, endpoint)

    def init_trove(self, name, api_version, engine, **kwargs):
        endpoint = kwargs.get('database')
        if not endpoint:
            endpoint = self.DEFAULT_ENDPOINTS['database']

        os_auth = kwargs.get('os_auth')
        if not isinstance(os_auth, dict):
            msg = _("The os_auth of '%s' services must be a list object") % engine
            raise fox_exc.FoxCloudException(msg)
        session = get_session(os_auth)

        self.trove = trove_client.TroveManager(name, api_version, session,
                                               engine, endpoint)

    def init_s3(self, name, api_version, engine, **kwargs):
        access_key = kwargs.get('access_key')
        secrete_key = kwargs.get('secrete_key')
        s3_endpoint = kwargs.get('s3_endpoint')
        region_name = kwargs.get('region_name')
        if access_key and secrete_key and s3_endpoint:
            self.s3 = storage_client.StorageManager(name_or_id=name, version=api_version,
                                                    session=None, engine=engine,
                                                    endpoint=s3_endpoint, access_key=access_key,
                                                    secret_key=secrete_key, region_name=region_name)
        else:
            msg = _("Cannot initialize services '%s', access_key and secrete_key and s3_endpoint "
                    "are not null") % engine
            raise fox_exc.FoxCloudException(msg)

    def init_shade(self, name, api_version, engine, **kwargs):
        os_auth = kwargs.get('os_auth')
        if not isinstance(os_auth, dict):
            msg = _("The os_auth of '%s' services must be a list object") % engine
            raise fox_exc.FoxCloudException(msg)
        session = get_session(os_auth)

        self.shade = shade_client.ShadeManager(name_or_id=name, version=api_version,
                                               session=session, engine=engine)

    def init_ldap(self, name, api_version, engine, **kwargs):
        ldap_endpoint = kwargs.get('ldap_endpoint')
        dn = kwargs.get('dn')
        password = kwargs.get('password')
        trace_level = kwargs.get('trace_level')

        self.ldap = ldap_client.LdapManager(name_or_id=name, version=api_version, engine=engine,
                                            endpoint=ldap_endpoint,  dn=dn, password=password,
                                            trace_level=trace_level)

    def set_default_endpoints(self, auth_url):
        try:
            url = urlparse(auth_url)
            self.DEFAULT_ENDPOINTS.update({
                'lbaas': '{}://{}:13876/v2'.format(url.scheme, url.hostname),
                'database': '{}://{}:8779/v1.0/'
                            'e26a8834af174274b7ca76f3ece03525'.format(url.scheme,
                                                                      url.hostname),
                'magnum': '{}://{}:9951/v1/'.format(url.scheme, url.hostname),
            })
        except Exception as e:
            pass

    def refresh(self, session, service_name):
        obj_class = getattr(self, service_name)
        if obj_class:
            obj_class.refresh(session)

    @property
    def api_version(self):
        return self._api_version

    @staticmethod
    def list_services():
        return SERVICES

    def __enter__(self):
        raise fox_exc.FoxCloudInvalidUsage(_(
            "FoxCloud can't be used as a context manager "
            "since it is redundant in case of SessionClient."))

    def __exit__(self, t, v, tb):
        # do not do anything
        pass
