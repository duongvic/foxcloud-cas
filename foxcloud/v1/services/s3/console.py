#
# Copyright (c) 2020 FTI-CAS
#

from boto3 import exceptions as aws_exc
from botocore.exceptions import ClientError
from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.s3 import base
from foxcloud.v1.utils.data_util import convert_size
from datetime import datetime
import json
# from foxcloud.v1.utils.reponse import response_model
# from foxcloud.v1.utils.reponse import to_dict
from foxcloud.v1.utils.reponse import Response
from foxcloud.config import CONF


class Console(base.BaseStorage, Response):
    __engine_type = 'console'

    # **********************************************
    #   Create a new resource
    # **********************************************
    def create_bucket(self, bucket_name, acl=None, lock=False):
        """
        Creates a new bucket.
        :param bucket_name:
        :param acl: [private, public-read, public-read-write, authenticated-read]
        :param lock:
        :return:
        """
        extra_params = {
            'ObjectLockEnabledForBucket': lock or False,
            'ACL': acl or 'private'
        }

        try:
            check_bucket = self.bucket_exists(bucket_name)
            if check_bucket:
                # raise fox_exc.FoxCloudBucketNameIsExists("Bucket name {} is exists.".format(name))
                raise Exception("Bucket name {} is exists.".format(bucket_name))
            self.api.create_bucket(Bucket=bucket_name, **extra_params)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(201, True)
            # response.data = {'lock': lock}
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)
        # return json.dump(response_model)

    def delete_object(self, bucket_name, key, version_id):
        """
        Removes the null version (if there is one) of an object and inserts a delete marker,
        which becomes the latest version of the object
        :param bucket_name:
        :param key: Object ID
        :param version_id:
        :return:
        """

        try:
            if version_id:
                self.api.delete_object(Bucket=bucket_name, Key=key, VersionId=version_id, MFA='',
                                       RequestPayer='requester', BypassGovernanceRetention=True)
            else:
                # check status bucket versioning
                # bucket_versioning = self.api_resource.BucketVersioning(bucket_name)
                # if bucket_versioning.status == 'Enabled':
                #     raise Exception("Bucket name {} is enabled versioning.".format(bucket_name))
                self.api.delete_object(Bucket=bucket_name, Key=key)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 204:
            response = Response(204, True)
            # response_model.code = 204
            # response_model.message = True
            # response_model.data = None
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def delete_object_all(self, bucket_name, keys):
        """
        Removes the null version (if there is one) of an object and inserts a delete marker,
        which becomes the latest version of the object
        :param bucket_name:
        :param keys: List Object ID
        :return:
        """

        try:
            for k in keys:
                # prefix = k.get('keys')
                prefix = k
                resp = self.api.list_objects(Bucket=bucket_name, Prefix=prefix, MaxKeys=1000)
                for obj in resp.get('Contents', []):
                    key = obj.get('Key')
                    # print(key)
                    self.api.delete_object(Bucket=bucket_name, Key=key)

            response = Response(204, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def bucket_exists(self, bucket_name):
        try:
            self.api.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            return False

    def folder_exists(self, bucket_name, folder_name):
        try:
            self.api.head_object(Bucket=bucket_name, Key=folder_name)
            return True
        except ClientError as e:
            return False

    def create_folder(self, bucket_name, folder_key):
        """
        Create folder in bucket
        :param bucket_name
        :param folder_key
        :return
        """
        try:
            folder = folder_key + "/"
            check_folder = self.folder_exists(bucket_name, folder)
            if check_folder:
                raise Exception("Folder name {} is exists.".format(folder_key))
            self.api.put_object(Bucket=bucket_name, Key=folder)
            response = Response(200, True)
        except ClientError as exp:
            raise exp
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def share_file(self, bucket_name, key, time):
        try:
            resp = self.api.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': key},
                                                   ExpiresIn=time)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(200, True)
            response.data = {'url': resp}
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def get_static_website(self, bucket_name, static_web_url):
        try:
            resp = self.api.get_bucket_website(Bucket=bucket_name)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(200, True)
            response.data = {'index': resp.get('IndexDocument').get('Suffix'),
                             'error': resp.get('ErrorDocument').get('Key'),
                             # 'url': "https://" + bucket_name + ".staticweb-s3dev.fptvds.vn/"}
                             # 'url': "https://" + bucket_name + CONF.STATIC_WEB}
                             'url': "https://" + bucket_name + static_web_url}
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def set_static_website(self, bucket_name, index_file, error_file, static_web_url):
        try:
            # set policy
            # version_policy = datetime.today().strftime('%Y-%m-%d')
            # version_policy = "2012-10-17"
            # bucket_policy = {
            #     "Version": version_policy,
            #     "Statement": [
            #         {
            #             'Sid': 'PublicReadGetObject',
            #             "Effect": "Allow",
            #             "Principal": "*",
            #             "Action": "s3:GetObject",
            #             # "Resource": "arn:aws:s3:::" + bucket_name + "/*"
            #             "Resource": "arn:aws:s3:::" + bucket_name + "/" + index_file
            #         }
            #     ]
            # }
            # bucket_policy = json.dumps(bucket_policy)
            # self.api.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

            # check file public
            permission_index = self.api.get_object_acl(Bucket=bucket_name, Key=index_file)
            if permission_index.get('Grants')[0].get('Grantee').get('Type') == 'CanonicalUser':
                raise Exception("Cannot set static file {} is private.".format(index_file))
            permission_error = self.api.get_object_acl(Bucket=bucket_name, Key=error_file)
            if permission_error.get('Grants')[0].get('Grantee').get('Type') == 'CanonicalUser':
                raise Exception("Cannot set static file {} is private.".format(error_file))

            # set static web
            website_configuration = {
                'ErrorDocument': {'Key': error_file},
                'IndexDocument': {'Suffix': index_file},
            }
            self.api.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_configuration)
            response = Response(200, True)
            # response.data = {'url': "https://" + bucket_name + ".staticweb-s3dev.fptvds.vn/"}
            # response.data = {'url': "https://" + bucket_name + CONF.STATIC_WEB}
            response.data = {'url': "https://" + bucket_name + static_web_url}
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def delete_static_website(self, bucket_name):
        try:
            # delete policy
            # self.api.delete_bucket_policy(Bucket=bucket_name)
            # delete config static web
            self.api.delete_bucket_website(Bucket=bucket_name)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 204:
            response = Response(204, True)
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def list_versioning(self, bucket_name, key):
        try:
            response = self.api.list_object_versions(Bucket=bucket_name, Prefix=key)
            result = {}
            data = []
            # for obj in [*response['Versions'], *response.get('DeleteMarkers', [])]:
            for obj in [*response['Versions']]:
                total_size = obj['Size']
                total_size = convert_size(total_size)
                item = {
                    'key': obj['Key'],
                    'lastModified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'versionId': obj['VersionId'],
                    'isLatest': obj['IsLatest'],
                    'size': total_size
                }
                data.append(item)
            result['data'] = data
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(200, True)
            response.data = result
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def list_objects(self, bucket_name, prefix=None):
        try:
            if prefix:
                # if not prefix.endswith("/"):
                #     prefix = prefix + '/'
                # response = s3.list_objects_v2(Bucket='tuan-bucket-19', Prefix="tuantd06/tuan02/", Delimiter='/')
                resp = self.api.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/', MaxKeys=1000)
            else:
                # response = s3.list_objects_v2(Bucket='tuan-bucket-19', Delimiter='/')
                resp = self.api.list_objects_v2(Bucket=bucket_name, Delimiter='/', MaxKeys=1000)

            data = []
            count = 0
            # get folder key
            for folder_obj in resp.get('CommonPrefixes', []):
                # print(folder_obj)
                folder_key = folder_obj['Prefix']
                folder_name = None
                if self._check_folder_name(folder_key):
                    folder_name = folder_key.split("/")[-2] if folder_key.split("/")[-1] == "" \
                        else folder_key.split("/")[0]
                item = {
                    'key': folder_key,
                    'folderName': folder_name,
                    'folder': True
                }
                data.append(item)
                count += 1

            # get file key
            get_last_modified = lambda i: int(i['LastModified'].strftime('%Y%m%d%H%M%S'))
            objs_sorted = sorted(resp.get('Contents', []), key=get_last_modified, reverse=True)
            for file_obj in objs_sorted:
                if file_obj.get('Key') != prefix:
                    # print(file_obj)
                    permission = self.api.get_object_acl(Bucket=bucket_name, Key=file_obj.get('Key'))
                    acl = True
                    if permission.get('Grants')[0].get('Grantee').get('Type') == 'CanonicalUser':
                        acl = False

                    total_size = file_obj['Size']
                    total_size = convert_size(total_size)
                    item = {
                        'key': file_obj['Key'],
                        'lastModified': file_obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                        'size': total_size,
                        # 'folder': folder,
                        # 'folderName': folder_name,
                        'acl': acl
                    }
                    data.append(item)
                    count += 1

            response = Response(200, True)
            # if len(data) == 0:
            #     response.data = {'prefix': prefix}
            # else:
            #     response.data = data
            response.data = data
            response.total = count
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def list_folder(self, bucket_name, prefix=None):
        try:
            if prefix:
                # response = self.api.list_objects(Bucket=bucket_name, Delimiter="/", Prefix=prefix + "/", MaxKeys=1000)
                response = self.api.list_objects(Bucket=bucket_name, Delimiter="/", Prefix=prefix, MaxKeys=1000)
            else:
                response = self.api.list_objects(Bucket=bucket_name, Delimiter="/", MaxKeys=100)
            # result = {}
            data = []
            for obj in response.get('CommonPrefixes', []):
                folder_key = obj['Prefix']
                item = {
                    'key': folder_key
                }
                data.append(item)
            response = Response(200, True)
            response.data = data
        except aws_exc.Boto3Error as e:
            raise fox_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def get_bucket_cors(self, bucket_name):
        try:
            resp = self.api.get_bucket_cors(Bucket=bucket_name)
            # if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            response = Response(200, True)
            response.data = resp['CORSRules']
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def get_lifecycle_cors(self, bucket_name):
        try:
            resp = self.api.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            response = Response(200, True)
            response.data = resp['Rules']
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def _check_folder_name(self, prefix):
        if "/" not in prefix:
            return False
        else:
            return True

    def get_policy(self, bucket_name):
        try:
            resp = self.api.get_bucket_policy(Bucket=bucket_name)
            # print(resp)
            dictPolicy = json.loads(resp['Policy'])
            effect = dictPolicy['Statement'][0]['Effect']
            response = Response(200, True)
            response.data = {'effect': effect}
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def set_policy(self, bucket_name, effect):
        try:
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        'Sid': 'PublicReadGetObject',
                        "Effect": effect,
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": "arn:aws:s3:::" + bucket_name + "/*"
                    }
                ]
            }
            # create policy
            bucket_policy = json.dumps(bucket_policy)
            resp = self.api.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
            # print(resp)
            response = Response(200, True)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def delete_policy(self, bucket_name):
        try:
            resp = self.api.delete_bucket_policy(Bucket=bucket_name)
            # print(resp)
            response = Response(200, True)
        except ClientError as e:
            raise e
        return response.to_dict(response)

    def get_quota_v2(self):
        try:
            # data = []
            sum_size = []
            sum_obj = []
            response = self.api.list_buckets()
            objs = response['Buckets']
            # sizeOfBucket = len(objs)    # total record bucket
            for item in objs:
                # get size bucket
                response = self.api.head_bucket(Bucket=item['Name'])
                total_size = int(response['ResponseMetadata']['HTTPHeaders']['x-rgw-bytes-used'])
                total_obj = int(response['ResponseMetadata']['HTTPHeaders']['x-rgw-object-count'])
                # total_size = convert_size(total_size)
                sum_size.append(total_size)
                sum_obj.append(total_obj)

            sum_sizes = sum(sum_size, 0)
            # sum_sizes = convert_size(sum_sizes)
            sum_objs = sum(sum_obj, 0)
            response = Response(200, True)
            response.data = {'sum_sizes': sum_sizes, 'sum_objs': sum_objs}

        except aws_exc.Boto3Error as e:
            raise aws_exc.FoxCloudException(e)
        except ClientError as e:
            raise e
        return response.to_dict(response)
