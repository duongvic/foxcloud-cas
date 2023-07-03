#
# Copyright (c) 2020 FTI-CAS
#

import ldap
import ldap.modlist

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud.v1.services import base as service_base


class LdapResource(fox_base.Resource):
    def add_details(self, info):
        """Normalize data information
        Subclass should be override this method
        :param info:
        :return:
        """
        self.data = info


class LdapManager(service_base.BaseChildManager):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.

    https://172.16.1.56:6443/  cn=admin,dc=ldap,dc=foxcloud,dc=vn / Cas@2020 thông in con đây anh @Khanh ạ
    """
    resource_class = LdapResource

    def __init__(self, name_or_id, version, engine, endpoint=None,
                 dn=None, password=None, trace_level=None):
        """
        Initialize LDAP
        :param name_or_id:
        :param version:
        :param engine:
        :param endpoint: URL of LDAP server
        :param dn: Distinguished name. For example: dn='cn=tester,dc=ldap,dc=foxcloud,dc=vn'
        :param password:
        :param trace_level:
        """
        super(LdapManager, self).__init__(name_or_id=name_or_id, api_version=version,
                                          engine=engine, endpoint=endpoint)
        if not self._is_supported():
            msg = _("Not supported engine '%s'. "
                    "Expected %s") % {self.engine, ' or '.join(e.upper()
                                                               for e in fox_base.SUPPORTED_ENGINES)}
            raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self.api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        error = None
        if self.engine == 'heat':
            pass
        if self.engine == 'console':
            try:
                from foxcloud.v1.services.ldap import console
                trace_level = trace_level or 0
                self._api = console.Console(uri=endpoint, trace_level=trace_level)
                self._api.simple_bind_s(who=dn, cred=password)
            except ldap.LDAPError as e:
                self._api = None
                error = e

        if not self._api:
            raise fox_exc.FoxCloudCreateException(resource=self.resource_class,
                                                  resource_id=engine,
                                                  extra_data=error)
        self._dn = dn
        self._password = password

    def _is_supported(self):
        return self.supported_heat if self.engine == 'heat' else self.supported_console

    @property
    def supported_heat(self):
        """Allow to do action by deploying heat stack
        Subclass should be override this method

        :return:
        """
        return False

    @property
    def supported_console(self):
        """Allow to do action by making http requests directly to openstack services
        Subclass should be override this method

        :return:
        """
        return True

    def whoami(self):
        """
        Get the distinguished name
        :return:
        """
        try:
            data = self._api.whoami_s()
            return self.resource_class(self, info=data)
        except ldap.LDAPError as e:
            raise fox_exc.FoxCloudException(e)

    def unbind(self):
        try:
            self._api.unbind_s()
        except ldap.LDAPError as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_user(self, dn, username, password):
        """
        Create a new user
        :param dn: Base distinguished name
        :param username:
        :param password:
        :return:
        """
        try:
            user_dn = 'cn={},{}'.format(username, dn)
            entry = {
                'objectClass': ['person'.encode('utf-8'), 'top'.encode('utf-8')],
                'cn': [username.encode('utf-8')],
                'sn': [username.encode('utf-8')],
                'userPassword': [password.encode('utf-8')],
            }
            msg_id = self._api.add_s(
              user_dn,
              ldap.modlist.addModlist(entry),
            )
            return self.resource_class(self, info=msg_id)
        except ldap.LDAPError as e:
            raise fox_exc.FoxCloudException(e)

    def add_to_group(self, user_dn, group_dn):
        """
        App user to group
        :param user_dn:
        :param group_dn:
        :return:
        """
        try:
            result = self._api.modify_s(dn=group_dn, modlist=[(ldap.MOD_ADD, "uniqueMember",
                                                               user_dn.encode('utf-8'))])
            return self.resource_class(self, info=result[0])
        except ldap.LDAPError as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Update an openstack resource being created
    # **********************************************
    def change_password(self, dn, old_password, new_password):
        """
        Change user's password
        :param dn: Distinguished name
        :param old_password:
        :param new_password:
        :return:
        """
        try:
            msg_id = self._api.passwd_s(dn, old_password, new_password)
            return self.resource_class(self, info=msg_id)
        except ldap.LDAPError as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************
    def delete_user(self, dn):
        """
        Delete an user
        :return:
        """
        try:
            msg_id = self._api.delete_s(dn)
            return self.resource_class(self, info=True)
        except ldap.LDAPError as e:
            raise fox_exc.FoxCloudException(e)
