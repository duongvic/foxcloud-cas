#
# Copyright (c) 2020 FTI-CAS
#
import sys

import boto3
from boto3 import exceptions as aws_exc
from botocore.exceptions import ClientError
from foxcloud.v1.utils.data_util import convert_size
from foxcloud.v1.utils.reponse import Response
# from foxcloud.v1.utils.reponse import response_model
# from foxcloud.v1.utils.reponse import to_dict
from foxcloud.config import CONF




class BaseStorage(Response):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    servers.
    """
    __engine_type__ = None

    S3_KEY_MAP = {
        'cache_control': 'CacheControl',
        'content_disposition': 'ContentDisposition',
        'content_encoding': 'ContentEncoding',
        'content_language': 'ContentLanguage',
        'content_length': 'ContentLength',
        'content_md5': 'ContentMD5',
        'content_type': 'ContentType',
        'expires': 'Expires',
        'server_encryption': 'ServerSideEncryption',
        'storage_class': 'StorageClass',
        'WebsiteRedirectLocation': 'WebsiteRedirectLocation',
        'customer_alg': 'SSECustomerAlgorithm',
        'customer_key': 'SSECustomerKey',
        'kms_key_id': 'SSEKMSKeyId',
        'kms_en_context': 'SSEKMSEncryptionContext',
        'ObjectLockRetainUntilDate': 'ObjectLockRetainUntilDate',
        'ObjectLockLegalHoldStatus': 'ObjectLockLegalHoldStatus',
        'prefix': 'Prefix',
        'encoding_type': 'EncodingType',
        'marker': 'Marker',
        'max_keys': 'MaxKeys',
        'Delimiter': 'delimiter',
    }
    S3_GRANT_KEYS = {
        'full_control': 'GrantFullControl',
        'read': 'GrantRead',
        'read_acp': 'GrantReadACP',
        'write': 'GrantWrite',
        'write_acp': 'GrantWriteACP',
    }

    def __init__(self, access_key, secret_key, endpoint, region_name=None):
        self._access_key = access_key
        self._secret_key = secret_key
        self.endpoint = endpoint
        # Use default session
        # s3 client
        self.api = boto3.client(service_name='s3', region_name=region_name,
                                endpoint_url=endpoint, aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key, verify=False)

        # s3 resource
        self.api_resource = boto3.resource(service_name='s3', region_name=region_name,
                                           endpoint_url=endpoint, aws_access_key_id=access_key,
                                           aws_secret_access_key=secret_key, verify=False)

    # **********************************************
    #   Fetch the information of resources
    # **********************************************
    # def get_bucket(self, bucket_name, fields=None):
    #     """
    #     Get a bucket information being created
    #     :param bucket_name:
    #     :param fields: (list) [acl, cors, encryption, lifecycle, policy, replication, tagging,
    #     website, notification]
    #     :return:
    #     """
    #     try:
    #         result = {}
    #         if fields:
    #             for field in fields:
    #                 func_call = getattr(self.api, 'get_bucket_{}'.format(field))
    #                 data = func_call(Bucket=bucket_name)
    #                 values_view = data.values()
    #                 value_iterator = iter(values_view)
    #                 result[field] = next(value_iterator) or {}
    #         else:
    #             status = self.api.get_bucket_accelerate_configuration(Bucket=bucket_name)
    #             result['status'] = status['ResponseMetadata']
    #             acl = self.api.get_bucket_acl(Bucket=bucket_name)
    #             result['acl'] = acl.get('ResponseMetadata') or {}
    #         return result
    #     except aws_exc.Boto3Error as e:
    #         return {}

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
    #     try:
    #         result = {}
    #         accelerate = self.api.get_bucket_accelerate_configuration(Bucket=bucket_name)
    #         result['accelerate'] = accelerate
    #         if analytic_id:
    #             analytics = self.api.get_bucket_analytics_configuration(Bucket=bucket_name, Id=analytic_id)
    #             result['analytics'] = analytics.get('AnalyticsConfiguration') or {}
    #
    #         if inventory_id:
    #             inventory = self.api.get_bucket_inventory_configuration(Bucket=bucket_name, Id=inventory_id)
    #             result['inventory'] = inventory.get('InventoryConfiguration') or {}
    #
    #         lifecycle = self.api.get_bucket_lifecycle_configuration(Bucket=bucket_name)
    #         result['lifecycle'] = lifecycle['Rules'] or []
    #
    #         if metric_id:
    #             metrics = self.api.get_bucket_metrics_configuration(Bucket=bucket_name, Id=metric_id)
    #             result['metrics'] = metrics.get('MetricsConfiguration') or {}
    #
    #         notification = self.api.get_bucket_notification_configuration(Bucket=bucket_name)
    #         result['notification'] = notification.get('TopicConfigurations') or []
    #         return result
    #     except aws_exc.Boto3Error as e:
    #         return {}

    def list_buckets(self, endpoint_url, bucket_name):
        """
        Returns a list of all buckets owned by the authenticated sender of the request.
        :return:
            {
                'Buckets': [
                    {
                        'Name': 'string',
                        'CreationDate': datetime(2015, 1, 1)
                    },
                ],
                'Owner': {
                    'DisplayName': 'string',
                    'ID': 'string'
                }
            }
        """
        try:
            data = []
            get_last_modified = lambda obj: int(obj['CreationDate'].strftime('%Y%m%d%H%M%S'))
            response = self.api.list_buckets()
            objs = response['Buckets']
            sizeOfBucket = len(objs)
            # sort bucket by CreationDate
            objs_sorted = sorted(objs, key=get_last_modified, reverse=True)
            for item in objs_sorted:
                access = False
                # get access bucket
                result = self.api.get_bucket_acl(Bucket=item['Name'])
                acl = len(result['Grants'])
                if acl > 1:
                    access = True
                # get size bucket
                response = self.api.head_bucket(Bucket=item['Name'])
                total_size = int(response['ResponseMetadata']['HTTPHeaders']['x-rgw-bytes-used'])
                total_size = convert_size(total_size)

                # response
                if bucket_name is None:
                    obj = {
                        'name': item['Name'],
                        'creationDate': item['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
                        'region': 'hn',
                        'access_bucket': access,
                        'total_size': total_size,
                        # 'endpoint': 'https://s3dev.fptvds.vn/' + item['Name']
                        # 'endpoint': CONF.ENDPOINT + item['Name']
                        'endpoint': endpoint_url + item['Name']

                    }
                    data.append(obj)
                else:
                    # search bucket_name
                    if bucket_name == item['Name']:
                        # print(bucket_name)
                        return [{
                            'name': item['Name'],
                            'creationDate': item['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
                            'region': 'hn',
                            'access_bucket': access,
                            'total_size': total_size,
                            # 'endpoint': 'https://s3dev.fptvds.vn/' + item['Name']
                            # 'endpoint': CONF.ENDPOINT + item['Name']
                            'endpoint': endpoint_url + item['Name']
                            }]

            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(200, True)
            response.data = data
            response.total = sizeOfBucket
        except aws_exc.Boto3Error as e:
            # return []
            raise aws_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    # def get_object(self, bucket_name, key, **kwargs):
    #     """Retrieves objects from S3.
    #     :param bucket_name: The bucket name containing the object.
    #     :param key: Key of the object to get.
    #     :param kwargs:
    #     :return:
    #     """
    #     try:
    #         return self.api.get_object(Bucket=bucket_name, Key=key, **kwargs)
    #     except aws_exc.Boto3Error as e:
    #         return {}

    # def get_object_field(self, bucket_name, fields, key, **kwargs):
    #     """
    #     Retrieves objects from S3.
    #     :param bucket_name:
    #     :param fields: [acl, legal_hold, lock_configuration, retention, tagging, torrent]
    #     :param key:
    #     :return:
    #     """
    #     try:
    #         extra_params = {}
    #         version_id = kwargs.get('version_id')
    #         if version_id:
    #             extra_params['VersionId'] = version_id
    #
    #         request_payer = kwargs.get('request_payer')
    #         if request_payer:
    #             extra_params['RequestPayer'] = request_payer
    #
    #         result = {}
    #         if fields:
    #             for field in fields:
    #                 func_call = getattr(self.api, 'get_object_{}'.format(field))
    #                 data = func_call(Bucket=bucket_name, Key=key, **extra_params)
    #                 result[field] = data
    #         return result
    #     except aws_exc.Boto3Error as e:
    #         return {}

    # def list_objects(self, bucket_name, **kwargs):
    #     """
    #     Get some or all (up to 1,000) of the objects in a bucket.
    #     :param bucket_name:
    #     :param kwargs:
    #     :return:
    #     """
    #     extra_params = {}
    #     for key, val in kwargs.items():
    #         extra_params[self.S3_KEY_MAP[key]] = val
    #
    #     try:
    #         return self.api.list_objects(Bucket=bucket_name, **extra_params)
    #     except aws_exc.Boto3Error as e:
    #         return {}

    # def list_objects_v2(self, bucket_name, **kwargs):
    #     """
    #     Get some or all (up to 1,000) of the objects in a bucket.
    #     :param bucket_name:
    #     :param kwargs:
    #     :return:
    #     """
    #     extra_params = {}
    #     for key, val in kwargs.items():
    #         extra_params[self.S3_KEY_MAP[key]] = val
    #
    #     try:
    #         return self.api.list_objects_v2(Bucket=bucket_name, **extra_params)
    #     except aws_exc.Boto3Error as e:
    #         return {}

    # def list_object_versions(self, bucket_name, **kwargs):
    #     """
    #     Get  all of the versions of objects in a bucket.
    #     :param bucket_name:
    #     :param kwargs:
    #     :return:
    #     """
    #     extra_params = {}
    #     for key, val in kwargs.items():
    #         extra_params[self.S3_KEY_MAP[key]] = val
    #
    #     version_id_marker = kwargs.get('version_id_marker')
    #     if version_id_marker:
    #         extra_params['VersionIdMarker'] = version_id_marker
    #
    #     try:
    #         return self.api.list_object_versions(Bucket=bucket_name, **extra_params)
    #     except aws_exc.Boto3Error as e:
    #         return {}
