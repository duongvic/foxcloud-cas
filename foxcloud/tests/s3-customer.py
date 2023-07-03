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
    # s3 policy create customerssss
    # s3 nghiatd@fpts.com.vn
    s3 = boto3.client('s3',
                      endpoint_url='https://ss-hn.fptvds.vn',
                      aws_access_key_id='26VH0X85UKEIE41H9HDD',
                      aws_secret_access_key='Bm7j5J0CfWc9Mcvd9RbZxYnQSb7CTtUUB02hdVEP')

    # production
    # s3 = boto3.client('s3',
    #                   endpoint_url='https://ss-hn.fptvds.vn',
    #                   aws_access_key_id='pj7lKSEXi16l3G',
    #                   aws_secret_access_key='nDou3mgjmY5J2zWXvS2sdTYIkfSaq1H5x7NcOFLp')

    # bucket_name = 'filestore5'
    bucket_name = 'login.fpts.com.vn'
    # bucket_name = 'file.fpts.com.vn'

    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                # 'Sid': 'AddPerm',
                'Sid': 'PublicReadGetObject',
                "Effect": "Allow",
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

    # get policy
    # result = s3.get_bucket_policy(Bucket=bucket_name)
    # print(result)

    # del policy
    # result = s3.delete_bucket_policy(Bucket=bucket_name)
    # print(result)

    # get list bucket
    # response = s3.list_buckets()
    # print(response)
    # for item in response['Buckets']:
    #     print(item['CreationDate'], item['Name'])
    #     print(item)

    # static web
    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
        # 'RedirectAllRequestsTo': {
        #     'HostName': 'login.fpts.com.vn',
        #     # 'Protocol': 'http'
        # },
        # 'RoutingRules': [
        #     {
        #         # 'Condition': {
        #         #     # 'HttpErrorCodeReturnedEquals': 'string',
        #         #     # 'KeyPrefixEquals': 'string'
        #         # },
        #         'Redirect': {
        #             'HostName': 'login.fpts.com.vn',
        #             # 'HttpRedirectCode': 'string',
        #             # 'Protocol': 'http',
        #             # 'ReplaceKeyPrefixWith': 'string',
        #             # 'ReplaceKeyWith': '/index.html'
        #         }
        #     },
        # ]
    }
    #
    request = s3.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_configuration)
    print(request)

    # result = s3.get_bucket_website(Bucket=bucket_name)
    # print(result)

    # response = s3.delete_bucket_website(Bucket=bucket_name)
    # print(response)


if __name__ == '__main__':
    main()
