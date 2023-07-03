#
# Copyright (c) 2020 FTI-CAS
#

import rados
import rbd

from foxcloud import exceptions as fox_exc


class BaseCeph(object):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    Refer: https://docs.ceph.com/docs/mimic/rbd/api/librbdpy/
    """
    __engine_type__ = None

    def __init__(self, config_file=None, keyring=None, pool=None):
        """
        Initialize
        :param config_file:
        :param pool:
        """
        try:
            self._cluster = rados.Rados(conffile=config_file,
                                        conf=dict(keyring=keyring))
            self._cluster.connect(timeout=10)
            self.pool = pool
            self.config_file = config_file
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def refresh(self, session):
        """
        :param session:
        :return:
        """

    def close(self):
        try:
            self._cluster.shutdown()
        except:
            pass

    # **********************************************
    #   Fetch the information of resources
    # **********************************************

    # **********************************************
    #   Rollback to a specific resource being created
    # **********************************************
    def rollback_snapshot(self, volume_id, snapshot_id):
        """
        Rollback to specific snapshot being created
        :param volume_id:
        :param snapshot_id:
        :return:
        """
        try:
            with self._cluster.open_ioctx(self.pool) as io_ctx:
                image_name = 'volume-{}'.format(volume_id)
                with rbd.Image(io_ctx, image_name) as image:
                    snapshot_name = 'snapshot-{}'.format(snapshot_id)
                    image.rollback_to_snap(snapshot_name)
                    return True
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def rollback_backup(self, volume_id, backup_id):
        """
        Rollback to specific backup being created
        :param volume_id:
        :param backup_id:
        :return:
        """
        try:
            with self._cluster.open_ioctx(self.pool) as io_ctx:
                image_name = 'volume-{}'.format(volume_id)
                with rbd.Image(io_ctx, image_name) as image:
                    backup_name = 'backup.{}'.format(backup_id)
                    image.rollback_to_snap(backup_name)
                    return True
        except Exception as e:
            raise fox_exc.FoxCloudException(e)