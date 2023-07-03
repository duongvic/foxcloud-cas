#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.v1.services import base as service_base


class StorageResource(fox_base.Resource):
    """

    """


class StorageManager(service_base.BaseChildManager):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating servers.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy
    """
    resource_class = StorageResource

    def __init__(self, name_or_id, version, api_version, session, engine, endpoint,
                 access_key, secret_key, region_name=None):
        super(StorageManager, self).__init__(name_or_id=name_or_id, version=version, api_version=api_version,
                                             session=session, engine=engine, endpoint=endpoint, access_key=access_key,
                                             secret_key=secret_key, region_name=region_name)
        # if not self._is_supported():
        #     msg = _("Not supported engine '%s'. " "Expected %s") % {self.engine, ' or ' .join(e.upper() for e in fox_base.SUPPORTED_ENGINES)}
        #     raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self._api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        if self.engine == 'heat':
            from foxcloud.v1.services.s3 import heat
            self._api = heat.Heat(access_key=access_key, secret_key=secret_key,
                                  endpoint=endpoint, region_name=region_name)
        if self.engine == 'console':
            from foxcloud.v1.services.s3 import console
            self._api = console.Console(access_key=access_key, secret_key=secret_key,
                                        endpoint=endpoint, region_name=region_name)
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
        """Allow to do action by making http requests directly to
        openstack services
        Subclass should be override this method

        :return:
        """
        return True

    # **********************************************
    #   Fetch the information of resources
    # **********************************************
    # def get_bucket(self, bucket_name, fields=None):
    #     """
    #     Get a bucket information being created
    #     :param bucket_name:
    #     :param fields: (list) [acl, cors, encryption, lifecycle, policy,
    #     replication, tagging,
    #     website, notification]
    #     :return:
    #     """
    #     data = self._api.get_bucket(bucket_name, fields)
    #     return self.resource_class(self, info=data)

    # def get_bucket_config(self, bucket_name, analytic_id=None, inventory_id=None,
    #                       metric_id=None):
    #     """
    #     Get all bucket configurations
    #     :param bucket_name:
    #     :param analytic_id:
    #     :param inventory_id:
    #     :param metric_id:
    #     :return:
    #     """
    #     data = self._api.get_bucket_config(bucket_name, analytic_id, inventory_id,
    #                                        metric_id)
    #     return self.resource_class(self, info=data)

    def list_buckets(self, endpoint_url, bucket_name=None):
        """
        Returns a list of all buckets owned by the authenticated sender of
        the request.
        :param bucket_name
        :param endpoint_url
        :return:
        """
        # data = self.list_buckets()
        data = self._api.list_buckets(endpoint_url, bucket_name)
        return self.resource_class(self, info=data)

    # @valid_kwargs('IfMatch', 'IfNoneMatch', 'Range', 'VersionId', 'RequestPayer',
    #               'PartNumber')
    # def get_object(self, bucket_name, key, **kwargs):
    #     """
    #     Retrieves objects from Amazon S3.
    #     :param bucket_name:
    #     :param key:
    #     :param kwargs:
    #     :return:
    #     """
    #     data = self._api.get_object(bucket_name, key, **kwargs)
    #     return self.resource_class(self, info=data)

    # @valid_kwargs('version_id', 'request_payer')
    # def get_object_field(self, bucket_name, fields, key, **kwargs):
    #     """
    #     Retrieves objects from S3.
    #     :param bucket_name:
    #     :param fields: [acl, legal_hold, lock_configuration, retention, tagging,
    #     torrent]
    #     :param key:
    #     :param kwargs:
    #     :return:
    #     """
    #     data = self.get_object_field(bucket_name, fields, key, **kwargs)
    #     return self.resource_class(self, info=data)

    # @valid_kwargs('delimiter', 'encoding_type', 'marker', 'max_keys', 'prefix',
    #               'request_payer')
    # def list_objects(self, bucket_name, **kwargs):
    #     """
    #     Get some or all (up to 1,000) of the objects in a bucket.
    #     :param bucket_name:
    #     :param kwargs:
    #     :return:
    #     """
    #     data = self.list_objects(bucket_name, **kwargs)
    #     return self.resource_class(self, info=data)

    # @valid_kwargs('delimiter', 'encoding_type', 'marker', 'max_keys', 'prefix',
    #               'continuation_token', 'fetch_owner', 'start_after', 'request_payer')
    # def list_objects_v2(self, bucket_name, **kwargs):
    #     """
    #     Get some or all (up to 1,000) of the objects in a bucket.
    #     :param bucket_name:
    #     :param kwargs:
    #     :return:
    #     """
    #     data = self._api.list_objects_v2(bucket_name, **kwargs)
    #     return self.resource_class(self, info=data)

    # @valid_kwargs('delimiter', 'encoding_type', 'marker', 'max_keys', 'prefix',
    #               'version_id_marker')
    # def list_object_versions(self, bucket_name, **kwargs):
    #     """
    #     all of the versions of objects in a bucket.
    #     :param bucket_name:
    #     :param kwargs:
    #     :return:
    #     """
    #     data = self.list_object_versions(bucket_name, **kwargs)
    #     return self.resource_class(self, info=data)

    # **********************************************
    #   Create a new resource
    # **********************************************

    def create_bucket(self, bucket_name, acl=None, lock=False):
        """
        Creates a new bucket.
        :param bucket_name:
        :param acl: [private, public-read, public-read-write, authenticated-read]
        :param permissions:
        {
            'full_control': '',
            'read': '',
            'read_acp': ''
            'write': '',
            'write_acp': ''
        }
        :param lock:
        :return:
        """
        data = self._api.create_bucket(bucket_name, acl, lock)
        return self.resource_class(self, info=data)

    def download_file(self, bucket_name, key, version_id=None):
        """
        Download a file
        :param bucket_name:
        :param key:
        :param version_id:
        :return:
        """
        data = self._api.download_file(bucket_name, key, version_id)
        return self.resource_class(self, info=data)

    def upload_file(self, bucket_name, key, acl, file_name, content_type):
        """
        Adds an object to a bucket
        :param bucket_name: Bucket name to which the PUT operation was initiated.
        :param key: Object key for which the PUT operation was initiated.
        :param acl:  The canned ACL to apply to the object.
        :param file_name:
        :param content_type:
        :return:
        """
        data = self._api.put_object(bucket_name, key, acl, file_name, content_type)
        return self.resource_class(self, info=data)

    def copy_object(self, src_bucket, src_key, des_bucket, des_key, version_id=None):
        """
        Creates a copy of an object that is already stored in S3.
        :param src_bucket: Source Bucket
        :param src_key:
        :param des_bucket: The name of the destination bucket, key name of the source object,
         and optional version ID of the destination object.
        :param des_key: The canned ACL to apply to the object.
        :param version_id:
        :return:
        """

        data = self._api.copy_object(src_bucket, src_key, des_bucket, des_key, version_id)
        return self.resource_class(self, info=data)

    # **********************************************
    #   Delete an resource being created
    # **********************************************
    def delete_bucket(self, bucket_name):
        """
        Deletes the bucket
        :param bucket_name:
        :return:
        """
        data = self._api.delete_bucket(bucket_name)
        return self.resource_class(self, info=data)

    def delete_object(self, bucket_name, key, version_id=None):
        """
        Removes the null version (if there is one) of an object and inserts a delete marker,
        which becomes the latest version of the object
        :param bucket_name:
        :param key: Object ID
        :param version_id:
        :return:
        """
        data = self._api.delete_object(bucket_name, key, version_id)
        return self.resource_class(self, info=data)

    def delete_object_all(self, bucket_name, keys):
        data = self._api.delete_object_all(bucket_name, keys)
        return self.resource_class(self, info=data)

    def create_folder(self, bucket_name, folder_key):
        """
        Create folder in bucket
        :param bucket_name
        :param folder_key
        :return
        """
        data = self._api.create_folder(bucket_name, folder_key)
        return self.resource_class(self, info=data)

    def permission_object(self, bucket_name, acl, key=None):
        data = self._api.permission_object(bucket_name, acl, key)
        return self.resource_class(self, info=data)

    def share_file(self, bucket_name, key, time):
        data = self._api.share_file(bucket_name, key, time)
        return self.resource_class(self, info=data)

    def get_lifecycle(self, bucket_name):
        data = self._api.get_lifecycle_cors(bucket_name)
        return self.resource_class(self, info=data)

    def set_lifecycle(self, bucket_name, objs):
        data = self._api.set_lifecycle(bucket_name, objs)
        return self.resource_class(self, info=data)

    def edit_lifecycle(self, bucket_name, obj):
        data = self._api.edit_lifecycle(bucket_name, obj)
        return self.resource_class(self, info=data)

    def delete_lifecycle(self, bucket_name, config_id=None):
        data = self._api.delete_lifecycle(bucket_name, config_id)
        return self.resource_class(self, info=data)

    def get_static_website(self, bucket_name, static_web_url):
        data = self._api.get_static_website(bucket_name, static_web_url)
        return self.resource_class(self, info=data)

    def set_static_website(self, bucket_name, index_file, error_file, static_web_url):
        data = self._api.set_static_website(bucket_name, index_file, error_file, static_web_url)
        return self.resource_class(self, info=data)

    def delete_static_website(self, bucket_name):
        data = self._api.delete_static_website(bucket_name)
        return self.resource_class(self, info=data)

    def get_cors(self, bucket_name):
        data = self._api.get_bucket_cors(bucket_name)
        return self.resource_class(self, info=data)

    def edit_cors(self, bucket_name, obj):
        data = self._api.edit_cors(bucket_name, obj)
        return self.resource_class(self, info=data)

    def set_cors(self, bucket_name, objs):
        data = self._api.set_cors(bucket_name, objs)
        return self.resource_class(self, info=data)

    def delete_cors(self, bucket_name, config_id=None):
        data = self._api.delete_cors(bucket_name, config_id)
        return self.resource_class(self, info=data)

    def set_versioning(self, bucket_name, status):
        data = self._api.set_versioning(bucket_name, status)
        return self.resource_class(self, info=data)

    def list_versioning(self, bucket_name, key):
        data = self._api.list_versioning(bucket_name, key)
        return self.resource_class(self, info=data)

    def list_objects(self, bucket_name, prefix=None):
        data = self._api.list_objects(bucket_name, prefix)
        return self.resource_class(self, info=data)

    def list_folder(self, bucket_name, prefix=None):
        data = self._api.list_folder(bucket_name, prefix)
        return self.resource_class(self, info=data)

    def get_policy(self, bucket_name):
        data = self._api.get_policy(bucket_name)
        return self.resource_class(self, info=data)

    def set_policy(self, bucket_name, effect):
        data = self._api.set_policy(bucket_name, effect)
        return self.resource_class(self, info=data)

    def delete_policy(self, bucket_name):
        data = self._api.delete_policy(bucket_name)
        return self.resource_class(self, info=data)

    def get_quota(self):
        # data = self._api.get_quota()
        data = self._api.get_quota_v2()
        return self.resource_class(self, info=data)
