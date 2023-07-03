#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud.v1.services import base as service_base


class CephResource(fox_base.Resource):
    pass


class CephManager(service_base.BaseChildManager):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    resource_class = CephResource

    def __init__(self, name_or_id, version, session=None, engine='console',
                 endpoint=None, config_file=None, keyring=None, pool=None):
        super(CephManager, self).__init__(name_or_id, version, session,
                                          engine, endpoint)
        if not self._is_supported():
            msg = _("Not supported engine '%s'. Expected %s") \
                  % {self.engine, ' or '.join(e.upper()
                                              for e in fox_base.SUPPORTED_ENGINES)}
            raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self.api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        if self.engine == 'heat':
            from foxcloud.v1.services.ceph import heat
            self._api = heat.Heat(config_file=config_file, keyring=keyring,
                                  pool=pool)
        if self.engine == 'console':
            from foxcloud.v1.services.ceph import console
            self._api = console.Console(config_file=config_file, keyring=keyring,
                                        pool=pool)
        if not self._api:
            raise fox_exc.FoxCloudCreateException(resource=self.resource_class,
                                                  resource_id=engine)

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

    # **********************************************
    #   Rollback to a specific resource being created
    # **********************************************

    def rollback_snapshot(self, volume_id, snapshot_id):
        """
        Rollback to a specific snapshot
        :param volume_id:
        :param snapshot_id:
        :return:
        """
        data = self._api.rollback_snapshot(volume_id, snapshot_id)
        return self.resource_class(self, info=data)
