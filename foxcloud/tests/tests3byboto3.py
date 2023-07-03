# -*- coding: utf-8 -*-
# encoding=utf8
import boto3
import logging
from botocore.exceptions import ClientError
from argparse import ArgumentParser
import os
import mimetypes
import sys
import math
import json
import base64
# import urllib2
import io
from datetime import datetime
from foxcloud.v1.utils.str_util import gen_key
from boto3.session import Session
import requests
from mypy_boto3_iam import IAMServiceResource


# boto3.set_stream_logger(name='botocore')

def main():

    s3 = boto3.client('s3',
                      endpoint_url='https://s3dev.fptvds.vn',
                      aws_access_key_id='Y4Q7HCDDTZV7I8P11Y8W',
                      aws_secret_access_key='Gd4iM36BMMVoBF1L2sNgGCKrYope1N7arbtnofZ3', verify=False)

    s3res = boto3.resource('s3',
                           endpoint_url='https://s3dev.fptvds.vn',
                           aws_access_key_id='Y4Q7HCDDTZV7I8P11Y8W',
                           aws_secret_access_key='Gd4iM36BMMVoBF1L2sNgGCKrYope1N7arbtnofZ3', verify=False)
    # sys.setdefaultencoding('utf8')

    # get list bucket
    # response = s3.list_buckets()
    # print(response)
    # for item in response['Buckets']:
    #     print(item['CreationDate'], item['Name'])
    #     print(item)

    param = {
        'Bucket': 'tuan-bucket-14'
    }

    # get region
    # response = s3.get_bucket_location(**param)
    # print(response)

    # result = s3.get_bucket_location(Bucket='tuan-bucket-14')
    # print(result)

    # get info bucket
    # response = s3.head_bucket(Bucket='tuan-bucket-14')
    # print(response)
    #
    # response = s3.head_object(Bucket='tuan-bucket-4', Key='index.html')
    # print(response)
    # size = response['ContentLength']
    # print(size)
    #
    # bucket = s3res.Bucket('tuan-bucket-14')
    # total_size = 0
    # count_obj = 0
    # for k in bucket.objects.all():
    #     total_size += k.size
    #     count_obj += 1
    # print(total_size)
    # print(count_obj)
    #
    # size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    # i = int(math.floor(math.log(total_size, 1024)))
    # p = math.pow(1024, i)
    # s = round(total_size / p, 2)
    # print("%s %s" % (s, size_name[i]))
    #
    # response = s3.head_bucket(
    #     Bucket='tuan-bucket-14'
    # )
    #
    # print(response['ResponseMetadata']['HTTPHeaders']['x-rgw-bytes-used'])


    # create bucket
    # response = s3.create_bucket(
    #     Bucket='tuan-bucket-44',
    #     # CreateBucketConfiguration={
    #     #     'LocationConstraint': 'us',
    #     # },
    # )
    # print(response)

    # ACLs
    # result = s3.get_bucket_acl(Bucket='tuan-bucket-4')
    # print(result)
    # print(len(result['Grants']))

    # get list object
    # all_objects = s3.list_objects(Bucket='tuan-bucket-14')
    # print(all_objects)

    # get policy, before: create policy
    # result = s3.get_bucket_policy(Bucket='tuan-bucket-9')
    # print(result)

    # create bucket with object lock , ACLs ; use
    # object lock ko ho tro enable sau khi tao bucket
    extra_params = {
        'ObjectLockEnabledForBucket': False,
        'ACL': 'public-read'
    }

    # response = s3.create_bucket(Bucket='tuan-bucket-17', **extra_params)
    # print(response)

    # create folder
    # response = s3.put_object(Bucket='tuan-bucket-20', Key='tuantd5/')       # luu y co dau / va thu muc ko co dau cach
    # print(response)

    # enable versioning
    # bucket_versioning = s3res.BucketVersioning('tuan-bucket-4')
    # bucket_versioning.enable()
    # # bucket_versioning.suspend()
    # st = bucket_versioning.status
    # print(st)
    # res = s3.get_bucket_versioning(Bucket='tuan-bucket-4')
    # print(res)

    # check versionID khi enable versioning
    # res = s3.get_object(Bucket='tuan-bucket-4', Key='photo/test_ver.txt')
    # print(res)

    ## check list version, suspended van ra dc versionid
    # bucket_versioning = s3res.BucketVersioning('tuan-bucket-4')
    # print(bucket_versioning.status)
    # res = s3.get_object(Bucket='tuan-bucket-4', Key='index.html')
    # print(res)

    # get list versionID cua 1 file khi thay doi
    # versions = s3res.Bucket('tuan-bucket-4').object_versions.filter(Prefix='index.html')
    # for version in versions:
    #     obj = version.get()
    #     print(obj.get('VersionId'), obj.get('ContentLength'), obj.get('LastModified'))


    # download file theo version
    # cd /tmp/ check file
    # path = '/tmp/test.txt'
    # OQNVAAXY3VMpawfq8-l2n72x2xj0XwU
    # s3.download_file('tuan-bucket-4', 'photo/test_ver.txt', path, ExtraArgs={'VersionId': 'OQNVAAXY3VMpawfq8-l2n72x2xj0XwU'})

    # restore versionID cua 1 file (khoi phuc phien ban truoc do -> xoa ban moi nhat se nhan ban truoc do)
    # resp = s3.list_object_versions(Prefix='index.html', Bucket='tuan-bucket-4')
    # print(resp)
    #
    # for obj in [*resp['Versions'], *resp.get('DeleteMarkers', [])]:
    #     print(f"Key: {obj['Key']}")
    #     print(f"VersionId: {obj['VersionId']}")
    #     print(f"LastModified: {obj['LastModified']}")
    #     print(f"IsLatest: {obj['IsLatest']}")
    #     print(f"Size: {obj.get('Size', 0) / 1e6}")
    #
    # response = s3.delete_object(Bucket='tuan-bucket-14', Key='testcopy.txt', VersionId='t59X8CtA56eulLUQk2D.PKHC7S1wRye')
    # print(response)


    # delete object
    # response = s3.delete_object(Bucket='tuan-bucket-4', Key='photo/test_ver.txt', VersionId='arj.gkUt6c6JDW0T81OkEBGxSiDaajI')
    # response = s3.delete_object(Bucket='tuan-bucket-19', Key='test.txt')
    # print(response)

    # public folder, file
    # object = s3res.Bucket('my-website-a').Object('index.html')
    # object = s3res.Bucket('tuan-bucket-9').Object('staticWeb/test.txt')
    # object = s3res.Bucket('tuan-bucket-7').Object('test.txt')
    # object.Acl().put(ACL='public-read')
    # object.Acl().put(ACL='private')
    ## --> https://s3dev.fptvds.vn/tuan-bucket-4/photo/VM_MIQ.png

    # static web
    # check status
    # res = s3.get_bucket_website(Bucket='tuan-bucket-6')
    # print(res)

    # config bucket website
    # website_configuration = {
    #     'ErrorDocument': {'Key': 'error.html'},
    #     'IndexDocument': {'Suffix': 'index.html'},
    # }
    # res = s3.put_bucket_website(Bucket='tuan-bucket-9', WebsiteConfiguration=website_configuration)
    # print(res)

    # delete bucket website
    # response = s3.delete_bucket_website(
    #     Bucket='tuan-bucket-6',
    #     # ExpectedBucketOwner='string'
    # )
    # print(response)

    # upload file index, error,..
    # try:
    #     bucket = s3res.Bucket('tuan-bucket-9')
    #     response = bucket.upload_file(Filename='../../../tuan.html', Key='tuan.html')
    #     print(response)
    # except ClientError as e:
    #     logging.error(e)
    #     # return False
    # # return True

    # C2 upload file -> view file
    # try:
    #     response = s3.upload_file(
    #         # '../../../test.txt', 'tuan-bucket-14', 'testcopy.txt',
    #         '../../../test.txt', 'tuan-bucket-19', 'tuantd5/test.txt',              # loi font tieng viet
    #         # '../../../tuan.html', 'tuan-bucket-20', 'tuan fol/tuan.html',        #upload file vao thu muc tuantd1
    #         ExtraArgs={'ContentType': "text/html", 'ACL': 'public-read'}
    #     )
    #     print(response)
    #     # curpath = os.path.abspath(os.curdir)
    #     # print(curpath)
    # except ClientError as e:
    #     logging.error(e)

    # download file ko bi loi tieng viet, nhung view thi loi
    # bucket = s3res.Bucket('tuan-bucket-9')
    # res = bucket.download_file(Filename='test.txt', Key='test.txt')
    # print(res)

    # upload multifile
    # FE chon multi file xong truyen xuong BE 1 list file, for roi push toi bucket


    # upload file
    # object = s3res.Object('tuan-bucket-19', 'tuan8.png')
    # txt_data = b'This is the content of the file uploaded from python boto3'
    # fileName = os.path.join('/tmp/upload', 'anh_size_ao.png')
    # mimetype = mimetypes.guess_type(fileName)
    # result = object.put(Body=open(fileName, 'rb'), ContentType=mimetype[0], ACL='public-read')
    # res = result.get('ResponseMetadata')
    # print(res)

    # set public file -> truy cap test
    # object = s3res.Bucket('tuan-bucket-9').Object('testcopy.txt')
    # object = s3res.Bucket('tuan-bucket-7').Object('tuan.html')
    # object.Acl().put(ACL='private')
    # object.Acl().put(ACL='public-read')
    # object.Acl().put(ACL='public-read-write')
    # object.Acl().put(ACL='private')

    #
    # res = s3res.Object('tuan-bucket-8', 'test.txt').Acl().put(ACL='public-read')
    # res = s3res.Object('tuan-bucket-9', 'index.html').Acl().put(ACL='public-read')
    # res = s3res.Object('tuan-bucket-9', 'index.html').Acl().put(ACL='private')
    # print(res)

    # https://s3dev.fptvds.vn/tuan-bucket-8/test.txt
    # https://s3dev.fptvds.vn/tuan-bucket-4/index.html
    # res = s3.put_object(Bucket='tuan-bucket-7', Key='tuan.html', Body='../../../tuan.html')
    # res = s3.put_object_acl(Bucket='tuan-bucket-7', Key='testcopy.txt', Body='../../../testcopy.txt')
    # print(res)

    # upload folder gom nhieu file tu local
    # TODO loi khi file la tieng viet

    # print(sys.getdefaultencoding())
    # print(sys.getfilesystemencoding())
    # x = '\xc4\x90\xe1\xbb\x93ng h\xe1\xbb\x93 \xc4\x91\xe1\xba\xbfm ng\xc6\xb0\xe1\xbb\xa3c 1 ph\xc3\xbat.mp4'
    # y = 'Đồng hồ đếm ngược 1 phút.mp4'
    # # x = x.decode('utf-8')
    # x = x.decode('utf8', 'surrogateescape').encode('utf8', 'surrogateescape')
    # RAWOut = open(1, 'w', encoding='utf8', closefd=False)
    # print(x, file=RAWOut)
    # x = x.encode().decode('utf-8', 'ignore')
    # y = sys.stdout.buffer.write(x)
    # print("123", y)
    # y = unicode(x).encode('utf8')
    # print("123", y)
    # s = b'\xc4\x90'
    # s.decode('utf-8')
    # s.encode("utf-8").decode("utf-8")
    # print(s.decode('utf-8'))
    # print(s)
    # source = unicode(s, 'utf-8')
    # s.decode('utf8')
    # print(s.replace("\\/", "/").encode().decode('unicode_escape'))
    # B = '\u0048\u0065\u006C\u006C\u006F\t\u5316\u4EB1\t\u041f\u0440\u0438\u0432\u0435\u0442'
    # print(B.encode('utf-8').decode('utf-8'))

    # hien thi tieng viet
    # s = b'\xc4\x90'
    # print(s.decode('utf-8'))

    # try:
    #     bucket = s3res.Bucket('tuan-bucket-9')
    #     # root_path = 'D:/sample/'  # local folder for upload
    #     root_path = '../../../staticWeb'  # local folder for upload
    #     directory_name = 'test123'     # before: create folder bucket
    #     # for filename in os.listdir(root_path):
    #     #     print(filename)
    #
    #     for path, dirs, files in os.walk(root_path.encode('utf8')):
    #     # for path, dirs, files in os.walk(root_path):
    #         # path = path.replace("\\", "/")
    #         # directory_name = path.replace(root_path, "")
    #         # dest_path = path.replace(root_path, "")
    #         # __s3file = os.path.normpath(s3Path + '/' + dest_path + '/' + file)
    #         # print(type(file))
    #         for file in files:
    #             fileName = file.decode('utf-8')
    #             # print(type(fileName))
    #             mimetype, _ = mimetypes.guess_type(fileName)
    #             if mimetype is None:
    #                 print("none123")
    #                 raise Exception("Failed to guess mimetype")
    #             # file = file.decode('utf8','surrogateescape').encode('utf8','surrogateescape')
    #             # file = u' '.join(file).encode('utf-8')
    #             # file.encode('utf-8')
    #             # file = file.decode('utf8')
    #             if file is None:
    #                 print("12")
    #
    #             # bucket.upload_file(os.path.join(path, file), directory_name+'/'+fileName, ExtraArgs={'ContentType': mimetype})
    #
    #             # bucket.upload_file(os.path.join(path.decode("utf-8"), fileName), directory_name+'/'+fileName, ExtraArgs={'ContentType': mimetype})
    #             bucket.upload_file("/root/staticWeb/" + "b'\xc4\x90\xe1\xbb\x93ng h\xe1\xbb\x93 \xc4\x91\xe1\xba\xbfm ng\xc6\xb0\xe1\xbb\xa3c 1 ph\xc3\xbat.mp4' + u''",
    #                                'tuan-bucket-8', ExtraArgs={'ContentType': mimetype})
    #             my_object = bucket.Object(directory_name+'/'+file)
    #             print(my_object, " ...Success", my_object.content_type)
    #     # print(response)
    # except ClientError as e:
    #     logging.error(e)

    # set public file
    # object = s3res.Bucket('tuan-bucket-14').Object('testcopy.txt')
    # object.Acl().put(ACL='public-read')

    #check bucket name, key
    # bucket = s3res.Bucket('tuan-bucket-8')
    # my_object = bucket.Object('Đồng hồ đếm ngược 1 phút.mp4')
    # print(my_object, " ...Success")
    # object = s3res.Bucket('tuan-bucket-8').Object('Đồng hồ đếm ngược 1 phút.mp4')
    # object.Acl().put(ACL='public-read')

    # test
    # upload file index, error,..
    # try:
    #     bucket = s3res.Bucket('tuan-bucket-9')
    #     file = u' '.join(file).encode('utf-8').strip()
    #     response = bucket.upload_file(Filename='../../../staticWeb/Đồng hồ đếm ngược 1 phút.mp4 ', Key='Đồng hồ đếm ngược 1 phút.mp4')
    #     print(response)
    # except ClientError as e:
    #     logging.error(e)

    # tao link share trong 1h
    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-9', 'Key': 'test123/hello-world.js'}, ExpiresIn=1000)
    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-19', 'Key': 'ram.jpg'}, ExpiresIn=1000)
    # print(res)

    # IAM
    # iam = boto3.resource('iam')
    # access_key = iam.AccessKey('tuanuser', 'Y4Q7HCDDTZV7I8P11Y8W')
    # # print(access_key)
    # # response = access_key.deactivate()
    # # print(response)
    # access_key_pair = iam.AccessKeyPair('tuanuser', 'Y4Q7HCDDTZV7I8P11Y8W', 'secret')
    # print(access_key_pair)
    #
    # IAMServiceResource = Session().resource("iam")

    # CORS neu file public thi ko can CORS cung truy cap dc
    # CORS cho phep truy cap bucket voi nhung file public
    # bucket = s3res.Bucket('tuan-bucket-20')
    # bucket_cors = bucket.Cors()
    # # allowedMethods = []
    # # allowedMethods.append('GET')
    # # allowedMethods.append('POST')
    # # print(allowedMethods)
    # # allowedOrigins = '58.186.85.243'
    # config = {
    #     'CORSRules': [
    #         {
    #             'AllowedMethods': ['GET', 'POST'],
    #             # 'AllowedMethods': allowedMethods,
    #             # 'AllowedOrigins': [allowedOrigins],
    #             'AllowedOrigins': ['58.186.85.243', '58.186.85.244'],
    #             'AllowedHeaders': ['*'],
    #             'MaxAgeSeconds': 2000
    #             # share 2h
    #         },
    #         {
    #             'AllowedMethods': ['GET', 'POST', 'PUT'],
    #             # 'AllowedMethods': allowedMethods,
    #             # 'AllowedOrigins': [allowedOrigins],
    #             'AllowedOrigins': ['58.186.85.245', '58.186.85.246'],
    #             'AllowedHeaders': ['*'],
    #             'MaxAgeSeconds': 2000
    #             # share 1h
    #         }
    #     ]
    # }
    # bucket_cors.put(CORSConfiguration=config)


    # test cors
    # TODO ID random string 6
    data = []
    obj1 = {
                'ID': 'ad243',
                'AllowedMethods': ['GET', 'POST'],
                'AllowedOrigins': ['58.186.85.243', '58.186.85.244'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 2000
            }
    #
    obj2 = {
                'ID': '245',
                'AllowedMethods': ['GET', 'POST', 'PUT'],
                'AllowedOrigins': ['58.186.85.245', '58.186.85.246'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 2000
            }

    # obj3 = {
    #             'AllowedMethods': ['GET', 'POST'],
    #             'AllowedOrigins': ['58.186.85.243', '58.186.85.244'],
    #             'AllowedHeaders': ['*'],
    #             'MaxAgeSeconds': 2000
    #         }
    data.append(obj1)
    data.append(obj2)
    #
    # bucket = s3res.Bucket('tuan-bucket-20')
    # bucket_cors = bucket.Cors()
    config = {
        'CORSRules': data
    }
    # response = bucket_cors.put(CORSConfiguration=config)
    # print(response)

    # cors client
    # res = s3.put_bucket_cors(
    #     Bucket='tuan-bucket-20',
    #     CORSConfiguration=config)
    # print(res)

    # phai config enable CORS truoc
    # get list cors
    # res = s3.get_bucket_cors(Bucket='tuan-bucket-20')
    # print(res.get('CORSRules'))

    # datas = res.get('CORSRules')
    # # ssh:58.186.85.243  --> curl -X GET https://s3dev.fptvds.vn/tuan-bucket-9/testcopy.txt
    # for item in datas:
    #     if item.get('ID') == 'ad243':
    #         datas.remove(item)
    # print(datas)
    #
    # config = {
    #     'CORSRules': datas
    # }
    # response = bucket_cors.put(CORSConfiguration=config)
    # print(response)
    # res = s3.get_bucket_cors(Bucket='tuan-bucket-20')
    # print(res.get('CORSRules'))

    # delete config CORS
    # res = s3.delete_bucket_cors(Bucket='tuan-bucket-20')
    # print(res)

    # bucket = s3res.Bucket('tuan-bucket-9')
    # bucket_cors = bucket.Cors()
    # res = bucket_cors.delete()
    # print(res)

    # Lifecycle

    # extra_params = {
    #     'ObjectLockEnabledForBucket': True,
    #     'ACL': 'public-read'
    # }
    #
    # response = s3.create_bucket(Bucket='tuan-bucket-14', **extra_params)
    # print(response)

    # extra_params = {
    #     'ObjectLockEnabledForBucket': True,     # true --> auto bat versioning
    #     'ACL': 'public-read'
    # }
    #
    # response = s3.create_bucket(Bucket='tuan-bucket-11', **extra_params)
    # print(response)

    # Object true --> tu dong bat versioning
    # bucket_versioning = s3res.BucketVersioning('tuan-bucket-13')
    # bucket_versioning.enable()

    # config lifecycle
    # bucket_lifecycle = s3res.BucketLifecycle('tuan-bucket-14')
    # response = bucket_lifecycle.put(
    #     LifecycleConfiguration={
    #         'Rules': [
    #             {
    #                 'Expiration': {
    #                     'Days': 1
    #                 },
    #                 'ID': 'tuan100',
    #                 'Prefix': 'tuan100/',
    #                 'Status': 'Enabled',
    #                 # 'Status': 'Disabled',
    #                 'NoncurrentVersionExpiration': {
    #                     'NoncurrentDays': 1
    #                 },
    #                 'AbortIncompleteMultipartUpload': {
    #                     'DaysAfterInitiation': 1
    #                 }
    #             },
    #             {
    #                 'Expiration': {
    #                     'Days': 1
    #                 },
    #                 'ID': 'tuan101',
    #                 'Prefix': 'tuan101/',
    #                 # 'Status': 'Enabled',
    #                 'Status': 'Disabled',
    #                 'NoncurrentVersionExpiration': {
    #                     'NoncurrentDays': 1
    #                 },
    #                 'AbortIncompleteMultipartUpload': {
    #                     'DaysAfterInitiation': 1
    #                 }
    #             }
    #         ]
    #     }
    # )
    # print(response)

    # get config lifecycle
    # try:
    #     res = s3.get_bucket_lifecycle_configuration(Bucket='tuan-bucket-19')
    #     print(res["Rules"])
    # except ClientError as e:
    #     if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
    #         print(e)

    # for rule in res["Rules"]:
    #     if rule["ID"] == "tuantd03":
    #         print("a")

    # create, update, delete lifecycle
    data = []
    obj1 = {'Expiration': {
                        'Days': 1
                    }, "ID": "sadsado", "Prefix": "tuantd02/", "Status": "Enabled"}
    # obj2 = {'Expiration': {
    #                                 'Days': 2
    #                             }, "ID": "tuantd03", "Prefix": "tuantd03/", "Status": "Enabled"}
    data.append(obj1)
    # data.append(obj2)
    # response = s3.put_bucket_lifecycle_configuration(
    #     Bucket="tuan-bucket-19",
    #     LifecycleConfiguration={
    #         "Rules": data
    #     },
    # )
    # print(response)


    # response = s3.put_bucket_lifecycle_configuration(
    #     Bucket="tuan-bucket-19",
    #     LifecycleConfiguration={
    #         "Rules": [{'Expiration': {
    #                     'Days': 1
    #                 }, "ID": "tuantd02", "Prefix": "tuantd02/", "Status": "Enabled"},
    #             {'Expiration': {
    #                                 'Days': 2
    #                             }, "ID": "tuantd03", "Prefix": "tuantd03/", "Status": "Enabled"}
    #         ]
    #     },
    # )
    # print(response)

    # delete lifecycle
    # res = s3.delete_bucket_lifecycle(Bucket="tuan-bucket-19")
    # print(res)

    # test file upload len bucket10-11
    # TODO test time xem co xoa ko sau 16h30 ngay mai(13-14: test.txt, 14 folder: tuantest) --> ok

    # try:
    #     response = s3.upload_file(
    #         '../../../test.txt', 'tuan-bucket-13', 'test.txt',
    #         ExtraArgs={'ContentType': "text/html", 'ACL': 'public-read'}
    #     )
    #     print(response)
    # except ClientError as e:
    #     logging.error(e)


    # chi get object lock nhung bucket da dc bat tu dau
    # response = s3.get_object_lock_configuration(
    #     Bucket='tuan-bucket-11',
    #     # ExpectedBucketOwner='string'
    # )
    # print(response)

    # TODO multi part upload

    # policy
    # bucket_policy = s3.get_bucket_policy_status(Bucket='tuan-bucket-6')
    # bucket_policy = s3.get_bucket_policy(Bucket='tuan-bucket-6')
    # print(bucket_policy)

    # bucket_name = 'tuan-bucket-6'
    # bucket_policy = {
    #     "Version": "2012-10-17",
    #     "Statement": [
    #         {
    #             # 'Sid': 'AddPerm',
    #             'Sid': 'PublicReadGetObject',
    #             "Effect": "Allow",
    #             "Principal": "*",
    #             "Action": "s3:GetObject",
    #             "Resource": "arn:aws:s3:::tuan-bucket-6/*"
    #         }
    #     ]
    # }
    #
    # bucket_policy = json.dumps(bucket_policy)
    # res = s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
    # print(res)

    # payer

    # log
    # try:
    #     result = s3.get_bucket_logging(Bucket='tuan-bucket-20')
    #     print('tun123')
    #     print(result)
    # except ClientError as e:
    #     raise Exception("boto3 client error in get_bucket_logging_of_s3: " + e.__str__())
    # except Exception as e:
    #     raise Exception("Unexpected error in get_bucket_logging_of_s3 function: " + e.__str__())
    # return result

    # TODO
    # bug hien thi tieng viet tren file
    # bug ko doc duoc ten file tieng viet


    ### download
    # object = s3res.Object('tuan-bucket-19', 'ram.jpg')
    # response = object.get()
    # print(response)
    # body = response['Body']
    # # with io.FileIO('tuan123.jpg', 'w') as file:
    # #     for b in body._raw_stream:
    # #         file.write(b)
    # object_content = body.read()
    # print(object_content)

    ### copy file
    # copy_source = {
    #     'Bucket': 'tuan-bucket-19',
    #     'Key': 'tuantd01.png'
    #     # 'VersionId': None
    # }
    #
    # # copy_source['VersionId'] = '123'
    # bucket = s3res.Bucket('tuan-bucket-20')
    # bucket.copy(copy_source, 'tuantd5/tuantd01.png')

    # object = s3res.Bucket('tuan-bucket-20').Object('tuantd5/ram.jpg')
    # object.Acl().put(ACL='public-read')


    # search bucket name
    # s3_resource = boto3.resource('s3')
    # buckets = s3.list_buckets()['Buckets']
    # for bucket in buckets:
    #     bucket_name = bucket['Name']
    #     bucket_name_rq = 'tuan-bucket-200'
    #     if bucket_name_rq in bucket_name:   # so sanh == hoac in
    #         print(bucket_name)
    # TODO bug khi tim bucketname ko ton tai

    # get list folder cua 1 bucket
    # resp = s3.list_objects(Bucket='tuan-bucket-19', Delimiter="/", MaxKeys=1000)
    # resp = s3.list_objects(Bucket='tuan-bucket-19', Prefix='tuantd101/', MaxKeys=1000)
    # print(resp)
    # resp = s3.list_objects(Bucket='tuan-bucket-19', MaxKeys=1000)
    # resp = s3.list_objects(Bucket='tuan-bucket-19', Delimiter="/", Prefix='tuan101/', MaxKeys=1000)
    # resp = s3.list_objects(Bucket='tuan-bucket-19', Prefix='tuan101/', MaxKeys=1000)
    # resp = s3.list_objects(Bucket='tuan-bucket-19', MaxKeys=1000)
    # # resp = s3.list_objects(Bucket='tuan-bucket-19', Delimiter="/", Prefix='tuan06/tuan01/', MaxKeys=1000)
    # print(resp)

    # detele all
    # objs = [
    #     # {"key": 'tuan06/tuan01/ram.jpg'},
    #     {"key": 'tuan06/tuan01'},
    # ]
    # resp = s3.list_objects(Bucket='tuan-bucket-19', MaxKeys=1000)       # get all key
    # resp = s3.list_objects(Bucket='tuan-bucket-19', Prefix='tuan06/tuan01/ram.jpg', MaxKeys=1000)       # get all key trong folder tuantd06
    # print(resp.get('Contents', []))

    # for k in objs:
    #     prefix = k.get('key')
    #     # print(key)
    #     resp = s3.list_objects(Bucket='tuan-bucket-19', Prefix=prefix, MaxKeys=1000)       # get all key trong folder tuantd06
    #     # print(resp.get('Contents', []))
    #     for obj in resp.get('Contents', []):
    #         key = obj.get('Key')
    #         print(key)
    #         response = s3.delete_object(Bucket='tuan-bucket-19', Key=key)
    #         print(response.get('ResponseMetadata').get('HTTPStatusCode'))

    # print(resp.get('CommonPrefixes', []))
    # result = {}
    # data = []
    # for obj in resp.get('CommonPrefixes', []):
    #     folder_key = obj['Prefix']
    #     item = {
    #         'key': folder_key
    #     }
    #     data.append(item)
    # result['data'] = data
    # print(result)

    # check folder ton tai -> ok
    # resp = s3.head_object(Bucket='tuan-bucket-19', Key='tuan99/tuan02/')
    # print(resp)


    # static web test
    extra_params = {
        'ObjectLockEnabledForBucket': False,
        'ACL': 'public-read'
    }

    # response = s3.create_bucket(Bucket='my-website-a', **extra_params)
    # print(response)

    bucket_name = 'tuan-bucket-4'
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                # 'Sid': 'AddPerm',
                'Sid': 'PublicReadGetObject',
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::" + bucket_name + "/*"
            }
        ]
    }

    # bucket_policy = json.dumps(bucket_policy)
    # res = s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
    # print(res)

    # iam = boto3.resource('iam')
    # policy_version = iam.PolicyVersion('arn', 'version_id')
    # print(policy_version)
    # response = iam.get_policy(
    #     PolicyArn='arn:aws:iam::aws:policy/AWSLambdaExecute'
    # )
    # print(response['Policy'])

    # res = s3.put_bucket_website(
    #     Bucket='my-website',
    #     WebsiteConfiguration={
    #         'ErrorDocument': {'Key': 'error.html'},
    #         'IndexDocument': {'Suffix': 'index.html'},
    #     }
    # )
    # print(res)
    # --> https://my-website.staticweb-s3dev.fptvds.vn/

    # response = s3.delete_bucket_website(
    #     Bucket='my-website',
    # )
    # response = s3.get_bucket_website(Bucket='my-website')
    # print(response)

    ####
    bucket_name_test = 'tuan-bucket'
    # print("tuan")

    # result = s3.get_bucket_website(Bucket=bucket_name_test)
    # print(result)

    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
    }
    #
    # request = s3.put_bucket_website(Bucket=bucket_name_test, WebsiteConfiguration=website_configuration)
    # print(request)

    # response = s3.delete_bucket_website(Bucket=bucket_name_test)
    # response = s3.delete_bucket_website(Bucket='tuan-bucket-6')
    # print(response)

    # object = s3res.Bucket('my-website-a').Object('index.html')
    # object.Acl().put(ACL='private')
    # object.Acl().put(ACL='public-read')
    # day = datetime.today().strftime('%Y-%m-%d')
    # print(day)

    # object = s3res.Bucket('tuan-bucket-6').Object('mau2.png')
    # object.Acl().put(ACL='private')
    # object.Acl().put(ACL='public-read')
    # s3.delete_bucket_policy(Bucket='tuan-bucket-6')

    # object_acl = s3res.ObjectAcl('tuan-bucket-6', 'error.html')
    # print(object_acl)
    # response = s3.get_object_acl(
    #     Bucket='tuan-bucket-6',
    #     Key='mau2.png',
    # )
    # print(response.get('Grants')[0].get('Grantee').get('Type'))
    # # print('private = CanonicalUser')
    # if response.get('Grants')[0].get('Grantee').get('Type') == 'CanonicalUser':
    #     print("1")

    # paging
    # paginator = s3.get_paginator('list_objects')
    # page_iterator = paginator.paginate(Bucket='tuan-bucket-19',
    #                                    PaginationConfig={'MaxItems': 10})
    # print(page_iterator)

    # operation_parameters = {'Bucket': 'tuan-bucket-19', 'Prefix': 'foo/baz'}
    marker = None
    # page_iterator = paginator.paginate(Bucket='tuan-bucket-19', PaginationConfig={'PageSize': 2, 'MaxItems': 10,})
    # get_last_modified = lambda obj: int(page_iterator['LastModified'].strftime('%s'))
    # get_last_modified = lambda obj: int(obj['LastModified'].strftime('%Y%m%d%H%M%S'))
    # objs = s3.list_objects_v2(Bucket='tuan-bucket-19')['Contents']
    # keys = [obj['Key'] for obj in sorted(objs, key=get_last_modified, reverse=True)]
    # print(keys)

    # for page in page_iterator:
    #     for obj in page['Contents']:
    #         key = obj['Key']
    #         day = obj['LastModified']
    #         print(key, day)

    # for page in page_iterator:
    #     print(page['Contents'])
    # print(gen_key(6))


    # delete bucket new
    # bucket = s3res.Bucket('phuln998')
    # res = bucket.object_versions.all().delete()
    # res = bucket.delete()
    # print(res)

    ### link
    # Generate the URL to get 'key-name' from 'bucket-name'

    # import requests
    #
    # url = s3.generate_presigned_url(
    #     ClientMethod='get_object',
    #     Params={
    #         'Bucket': 'tuan-bucket-4',
    #         'Key': 'index.html'
    #     }
    # )
    #
    # # Use the URL to perform the GET operation. You can use any method you like
    # # to send the GET, but we will use requests here to keep things simple.
    # response = requests.get(url)
    # print(response)

    ###
    bucket_name = 'tuan-bucket-4'
    key_name = 'index.html'

    # s3_client = boto3.client('s3')
    # upload_details = s3.generate_presigned_post(bucket_name, key_name)

    # print(upload_details)

    # result = s3.get_bucket_policy(Bucket='tuan-bucket-9')
    # print(result)

    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-4', 'Key': 'index.html'}, ExpiresIn=10000)
    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-4', 'Key': 'index.html'}, ExpiresIn=10000, HttpMethod='DELETE')
    # res = s3.generate_presigned_url('delete_object', Params={'Bucket': 'tuan-bucket-4', 'Key': 'index.html'})
    # print(res)

    # response = s3.get_bucket_policy_status(
    #     Bucket='tuan-bucket-19',
    #     ExpectedBucketOwner='string'
    # )
    # print(response)

    # response = s3.delete_bucket_policy(Bucket='tuan-bucket-19')
    # print(response)

    # res = s3.generate_presigned_url('delete_objects', Params={'Bucket': 'tuan-bucket-4', 'Delete': {
    #         'Objects': [{'Key': 'index.html'}]
    #     }})
    # print(res)

    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-4', 'Key': 'index.html'}, ExpiresIn=10000)
    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-4', 'Key': 'error.html'}, ExpiresIn=0)
    # res = s3.generate_presigned_url('get_object', Params={'Bucket': 'tuan-bucket-4', 'Key': 'mau-don-sac-2.png'}, ExpiresIn=3600)
    # print(res)

#     url = s3.generate_presigned_url(
#     'get_object',
#      Params={
#         'Bucket': 'tuan-bucket-4',
#         'Key': 'index.html',
#         # 'SSECustomerKey': 'XAj1phRW0UtLFFdaX3iU3yUvXbY'
#         'ACL': 'private'
#     },
#     HttpMethod="GET",
#     # HttpMethod="DELETE",
# )
#     print(url)

    # bucket_request_payment = s3res.BucketRequestPayment('tuan-bucket-4')
    # print(bucket_request_payment)

    bucket_name = 'tuan-bucket-4'
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                # 'Sid': 'AddPerm',
                'Sid': 'PublicReadGetObject',
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::" + bucket_name + "/index.html"
            },
            {
                'Sid': 'PublicReadGetObject',
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::" + bucket_name + "/error.html"
            },
        ]
    }

    # bucket_policy = json.dumps(bucket_policy)
    # res = s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
    # print(res)
    # result = s3.get_bucket_policy(Bucket='tuan-bucket-4')
    # print(result)


    #### get permistion obj
    # object_acl = s3res.ObjectAcl('tuan-bucket-4', 'index.html')
    # print(len(object_acl.grants))

    ##
    # print(s3)
    # # print(s3res)
    # # create bucket
    # response = s3.create_bucket(
    #     Bucket='tuan2-bucket-44',
    #     # CreateBucketConfiguration={
    #     #     'LocationConstraint': 'us',
    #     # },
    # )
    # print(response)

    # response = s3.generate_presigned_post('tuan-bucket-9', 'index.html', ExpiresIn=3000)
    # print(response['url'])
    # print(response['fields'])


    # test delete object versioning
    # object = s3res.Object('tuan-bucket-15', 'index.html')
    # res = object.delete(
    #     MFA='',
    #     VersionId='D8ycPZRydDFjrPCUzkNFgPSSZ4IzPn3',
    #     RequestPayer='requester',
    #     BypassGovernanceRetention=True
    # )
    # print(res)

    # response = s3.delete_object(
    #     Bucket='tuan-bucket-15',
    #     Key='index.html',
    #     MFA='',
    #     VersionId='GD9uRgESOWLkifDeB9fD8LtXlFLHRhR',
    #     RequestPayer='requester',
    #     BypassGovernanceRetention=True
    # )
    # print(response)

    ## get versioning bucket
    # bucket_versioning = s3res.BucketVersioning('tuan-bucket-19')
    # print(bucket_versioning.status)

    # # list versioning
    # response = s3.list_object_versions(Bucket='tuan-bucket-15', Prefix='index.html')
    # print(response)

    # list object
    # response = s3.list_objects(Bucket='tuan-bucket-9', Delimiter="/", MaxKeys=1000)
    # print(response)

    #
    my_bucket = s3res.Bucket('tuan-bucket-19')
    # # for file in my_bucket.objects.all():
    # #     print(file.key)
    # for obj in my_bucket.objects.filter(Prefix=''):
    #     print(obj.key, )
    ## Bucket to use
    # bucket = s3.Bucket('my-bucket')

    ## List objects within a given prefix
    # for obj in my_bucket.objects.filter(Prefix='tuantd06/'):
    #     print(obj.key)

    # response = s3.list_objects(Bucket='tuan-bucket-19', Delimiter="/", MaxKeys=1000)
    # res = response

    # test
    # checked = "tuantd06/tuan02/tuan022/"
    # print(checked.count('/'))

    # # list object
    # # response = s3.list_objects_v2(Bucket='tuan-bucket-19', Prefix="tuantd06/tuan02/", Delimiter='/')
    # # response = s3.list_objects_v2(Bucket='tuan-bucket-19', Prefix="tuantd06/tuan02/tuan022/", Delimiter='/')
    # response = s3.list_objects_v2(Bucket='tuan-bucket-19', Delimiter='/')
    # # response = s3.list_objects_v2(Bucket='tuan-bucket-19', Prefix="tuantd06/", Delimiter='/')
    # # prefix_input = 'tuantd06/tuan02/tuan022/'
    # # prefix_input = 'tuantd06/tuan02/'
    # # prefix_input = 'tuantd06'
    # prefix_input = None
    #
    # for prefix1 in response.get('CommonPrefixes', []):
    #     print(prefix1)
    #     # print(prefix['Prefix'][:-1])
    # # for prefix2 in response.get('Contents', []):
    # #     # print(prefix2)
    # #     if prefix2.get('Key') != prefix_input:
    # #         print(prefix2)
    # str1 = "tuntd01/"
    # if not str1.endswith("/"):
    #     print(True)
    # else:
    #     print(False)

    # tuan - bucketxxx
    # get bucket object lock
    # response = s3.get_object_lock_configuration(
    #     Bucket='tuan-bucket-lock-true-1',
    #     # Bucket='tuan-bucket-15',
    #     # ExpectedBucketOwner='string'
    # )
    # print(response)

    # get object acl
    # response = s3.get_object_acl(
    #     Bucket='tuan-bucketxxx',
    #     Key='fti-k8s-cloud-network.jpeg',
    #     # VersionId='string',
    #     # RequestPayer='requester',
    #     # ExpectedBucketOwner='string'
    # )
    # print(response)

    # get user
    # client_sts = boto3.client("sts", aws_access_key_id='Y4Q7HCDDTZV7I8P11Y8W',
    #                   aws_secret_access_key='Gd4iM36BMMVoBF1L2sNgGCKrYope1N7arbtnofZ3')
    # account_id = client_sts.get_caller_identity()["Account"]
    # # res = s3res.get_caller_identity().get('Account')
    # print(account_id)

    # account_id = boto3.resource('iam').CurrentUser().arn.split(':')[4]
    # print(account_id)

    sts = boto3.client('sts',
                      endpoint_url='https://s3dev.fptvds.vn',
                      aws_access_key_id='Y4Q7HCDDTZV7I8P11Y8W',
                      aws_secret_access_key='Gd4iM36BMMVoBF1L2sNgGCKrYope1N7arbtnofZ3',
                      region_name='us',
                      verify=False
                       )
    # sts = boto3.client('sts', aws_access_key_id='Y4Q7HCDDTZV7I8P11Y8W',
    #                   aws_secret_access_key='Gd4iM36BMMVoBF1L2sNgGCKrYope1N7arbtnofZ3')
    #
    # sts_response = sts.get_session_token()
    # response = sts.get_caller_identity()
    # # response = sts.get_caller_identity()
    # print('User ID:', response['UserId'])

    # account_id = boto3.resource('iam',aws_access_key_id='Y4Q7HCDDTZV7I8P11Y8W',
    #                   aws_secret_access_key='Gd4iM36BMMVoBF1L2sNgGCKrYope1N7arbtnofZ3')
    # print(account_id.CurrentUser().arn.split(':')[4])


    # policy
    bucket_name = 'tuan-bucket-9'
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                # 'Sid': 'AddPerm',
                'Sid': 'PublicReadGetObject',
                # "Effect": "Allow",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::" + bucket_name + "/*"
                # "Resource": [
                #     # "arn:aws:s3:::DOC-EXAMPLE-BUCKET",
                #     "arn:aws:s3:::DOC-EXAMPLE-BUCKET/*",
                #     "arn:aws:s3:::DOC-EXAMPLE-BUCKET/*",
                #
                # ]
            }
        ]
    }

    # create policy
    # bucket_policy = json.dumps(bucket_policy)
    # res = s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
    # print(res)

    # result = s3.get_bucket_policy(Bucket='tuan-bucket-9')
    # print(result)


if __name__ == '__main__':
    main()
