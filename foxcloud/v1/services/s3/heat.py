#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.s3 import base
from boto3 import exceptions as aws_exc
from botocore.exceptions import ClientError
# from foxcloud.v1.utils.reponse import response_model
# from foxcloud.v1.utils.reponse import to_dict
# from foxcloud.v1.utils.str_util import gen_key
from foxcloud.v1.utils.reponse import Response


class Heat(base.BaseStorage, Response):
    """
    Not supported
    """
    __engine_type__ = 'heat'

    def download_file(self, bucket_name, key, version_id=None):
        """
        Download an S3 object to a file.
        :param bucket_name: The name of the bucket to upload to.
        :param version_id: The versionId of file.
        :param key: The name of the key to upload to.
        :return:
        """
        try:
            obj = self.api_resource.Object(bucket_name, key)
            if version_id:
                return obj.get(VersionId=version_id)
            return obj.get()

        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e

    def put_object(self, bucket_name, key, acl, file_name, content_type):
        """
        Adds an object to a bucket (upload file)
        :param bucket_name: Bucket name to which the PUT operation was initiated.
        :param key: Object key for which the PUT operation was initiated.
        :param acl:  The canned ACL to apply to the object.
        ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|
        'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
        :param bucket_name:
        :param key:
        :param acl:
        :param file_name:
        :param content_type:
        :return:
        """

        if acl:
            acl = acl or 'private'

        try:
            obj = self.api_resource.Object(bucket_name, key)
            obj.put(Body=file_name, ContentType=content_type, ACL=acl)
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def copy_object(self, src_bucket, src_key, des_bucket, des_key, version_id=None):
        """
        Creates a copy of an object that is already stored in S3.
        :param src_bucket: Source Bucket
        :param src_key:
        :param des_bucket: The name of the destination bucket, key name of the source object,
         and optional version ID of the destination object.
        :param des_key:
        :param version_id:
        :return:
        """
        try:
            copy_source = {
                'Bucket': src_bucket,
                'Key': src_key,
                # 'VersionId': 'string'
            }
            if version_id:
                copy_source['VersionId'] = version_id
            bucket = self.api_resource.Bucket(des_bucket)
            bucket.copy(copy_source, des_key)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def permission_object(self, bucket_name, acl, key):
        try:
            if key is not None:
                obj = self.api_resource.Bucket(bucket_name).Object(key)
            else:
                obj = self.api_resource.Bucket(bucket_name)
            obj.Acl().put(ACL=acl)
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def set_cors(self, bucket_name, objs):
        try:
            bucket = self.api_resource.Bucket(bucket_name)
            bucket_cors = bucket.Cors()
            data = []
            for obj in objs:
                # idx = gen_key(6)
                # obj['ID'] = gen_key(6)
                # obj['ID'] = idx
                data.append(obj)
            config = {
                'CORSRules': data
            }
            bucket_cors.put(CORSConfiguration=config)
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def edit_cors(self, bucket_name, obj):
        try:
            res = self.api.get_bucket_cors(Bucket=bucket_name)
            data = res.get('CORSRules')
            for item in data:
                if item.get('ID') == obj.get('ID'):
                    data.remove(item)

            data.append(obj)
            config = {
                'CORSRules': data
            }
            bucket = self.api_resource.Bucket(bucket_name)
            bucket_cors = bucket.Cors()
            bucket_cors.put(CORSConfiguration=config)
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def delete_cors(self, bucket_name, config_id):
        try:
            bucket = self.api_resource.Bucket(bucket_name)
            bucket_cors = bucket.Cors()
            if config_id is None:
                bucket_cors.delete()
            else:
                res = self.api.get_bucket_cors(Bucket=bucket_name)
                # print(res.get('CORSRules'))
                data = res.get('CORSRules')
                for item in data:
                    if item.get('ID') == config_id:
                        data.remove(item)
                # print(datas)
                config = {
                    'CORSRules': data
                }
                bucket_cors.put(CORSConfiguration=config)
            response = Response(204, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def set_lifecycle(self, bucket_name, objs):
        try:
            bucket_lifecycle = self.api_resource.BucketLifecycle(bucket_name)
            data = []
            for obj in objs:
                data.append(obj)
            config = {
                'Rules': data
            }
            bucket_lifecycle.put(LifecycleConfiguration=config)
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def edit_lifecycle(self, bucket_name, obj):
        try:
            res = self.api.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            data = res['Rules']
            for item in data:
                if item.get('ID') == obj.get('ID'):
                    data.remove(item)

            data.append(obj)
            config = {
                'Rules': data
            }
            bucket_lifecycle = self.api_resource.BucketLifecycle(bucket_name)
            bucket_lifecycle.put(LifecycleConfiguration=config)
            response = Response(200, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def delete_lifecycle(self, bucket_name, config_id):
        try:
            bucket_lifecycle = self.api_resource.BucketLifecycle(bucket_name)
            # bucket_lifecycle.delete()

            if config_id is None:
                bucket_lifecycle.delete()
            else:
                res = self.api.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                data = res.get('Rules')
                for item in data:
                    if item.get('ID') == config_id:
                        data.remove(item)
                config = {
                    'Rules': data
                }
                bucket_lifecycle.put(LifecycleConfiguration=config)

            response = Response(204, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def set_versioning(self, bucket_name, status):
        try:
            bucket_versioning = self.api_resource.BucketVersioning(bucket_name)
            bucket_versioning.suspend()
            if status:
                bucket_versioning.enable()
            response = Response(200, True)
            response.data = {'versioning': bucket_versioning.status}
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def delete_bucket(self, bucket_name):
        try:
            bucket = self.api_resource.Bucket(bucket_name)
            bucket.object_versions.all().delete()
            bucket.delete()
            response = Response(204, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def get_quota(self):
        try:
            total_sizes = []
            total_objs = []
            for bucket in self.api_resource.buckets.all():
                bucket_name = bucket.name

                total_size = 0
                count_obj = 0
                bucket = self.api_resource.Bucket(bucket_name)
                for k in bucket.objects.all():
                    total_size += k.size
                    count_obj += 1
                total_sizes.append(total_size)
                total_objs.append(count_obj)
            sum_sizes = sum(total_sizes, 0)
            sum_objs = sum(total_objs, 0)
            response = Response(204, True)
            response.data = {'sum_sizes': sum_sizes, 'sum_objs': sum_objs}
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)
