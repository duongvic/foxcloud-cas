from foxcloud.v1.services.s3 import client
import os
import mimetypes
from foxcloud.config import CONF
params = {
    'name_or_id': 'name_or_id',
    'version': '1',
    'api_version': '1',
    'session': None,
    # 'engine': 'HEAT',
    'engine': 'CONSOLE',
    'endpoint': 'http://ss.fptcompute.com.vn',
    'access_key': 'tuantdpw',
    'secret_key': '6SmJXpOgWgB6Wyoh9zqT77sN8ZnNfvqUgjA3sx9M',
    'region_name': 'us'
}
# endpoint_url = 'http://ss.fptcompute.com.vn',
# aws_access_key_id = 'tuantdpw',
# aws_secret_access_key = '6SmJXpOgWgB6Wyoh9zqT77sN8ZnNfvqUgjA3sx9M', verify = False)

params_create = {
    'bucket_name': 'tuan-bucket-22a',
    # 'region': 'us',
    # 'LocationConstraint': 'us',
    # 'acl': None,
    'acl': 'public-read',
    # 'permissions': None,
    'lock': False
}

objs = [
        # {"key": 'tuan06/tuan01/leesin.png'},
        {"keys": 'tuan.html'},
        {"keys": 'ram.jpg'},
    ]


def init_bucket():
    bucket = client.StorageManager(**params)
    return bucket


# show list bucket
def do_test_list_bucket():
    # bucket = client.StorageManager(**params)
    bucket = init_bucket()
    buckets = bucket.list_buckets()._info
    # buckets = bucket.list_buckets('tuan-bucket-20')._info

    # print("---tuantests3---")
    print(buckets)


# create bucket
def do_test_create_bucket():
    bucket = init_bucket()
    # bucket = bucket.create_bucket('tuan-bucket-3910i1')._info
    bucket = bucket.create_bucket('tuantdtd02','public-read',True)._info
    print(bucket)


def do_test_get_bucket():
    bucket = init_bucket()
    bucket.get_bucket_location('tuantd-105')


def do_test_delete_bucket():
    bucket = init_bucket()
    bucket.delete_bucket('phu767')


def do_test_create_folder():
    bucket = init_bucket()
    bucket = bucket.create_folder('tuan-bucket-19', 'tuan99/tuan033')._info
    print(bucket)


def do_test_upload_file():
    bucket = init_bucket()
    kwargs = {
        'ContentType': "text/html",
        'ACL': 'public-read'
    }
    bucket = bucket.upload_file('../../../tuan.html', 'tuan-bucket-20', 'tuantd5/tuan.html', **kwargs)._info
    print(bucket)


def do_test_download_file():
    bucket = init_bucket()
    bucket = bucket.download_file('tuan-bucket-19', 'ram.jpg', 'ram.jpg')._info
    # v2 download with version
    # path_download = '/tmp/tuan/test.txt'
    # bucket = bucket.download_file('tuan-bucket-4', 'photo/test_ver.txt', 'test_ver.txt', 'OQNVAAXY3VMpawfq8-l2n72x2xj0XwU')._info
    print(bucket)


def do_test_put_objet():
    bucket = init_bucket()
    fileName = os.path.join('/tmp/upload', 'anh_size_ao.png')
    mimetype = mimetypes.guess_type(fileName)
    contentType = mimetype[0]
    bucket = bucket.put_object('tuan-bucket-19', 'tuantd01.png', 'public-read', fileName, contentType)._info
    print(bucket)

def do_test_upload_file():
    bucket = init_bucket()
    bucket = bucket.delete_object('tuan-bucket-19', 'tuantd01.png')._info
    print(bucket)


def do_list_versioning():
    bucket = init_bucket()
    bucket = bucket.list_versioning('tuan-bucket-15', 'index.html')._info
    print(bucket)

def do_delete_file_versioning():
    bucket = init_bucket()
    # bucket = bucket.delete_object('tuan-bucket-15', 'index.html', 'IE-vYy8e6X9L5pRFjWuOSsrOJX3Tx31')._info
    bucket = bucket.delete_object('tuan-bucket-15', 'index.html')._info
    print(bucket)

def do_set_versioning():
    bucket = init_bucket()
    bucket = bucket.set_versioning('tuan-bucket-4', False)._info
    print(bucket)


def do_list_objects():
    bucket = init_bucket()
    bucket = bucket.list_objects('tuan-bucketxxx')._info
    # bucket = bucket.list_objects('tuan-bucket-19', 'tuantd06')._info
    # bucket = bucket.list_objects('tuan-bucket-19', 'tuantd777')._info
    # bucket = bucket.list_objects('tuan-bucket-19', 'tuantd06/tuan02/')._info
    print(bucket)

def do_list_folder():
    bucket = init_bucket()
    # bucket = bucket.list_folder('tuan-bucket-19')._info
    bucket = bucket.list_folder('tuan-bucket-14', 'tuan101/tuan1022/')._info
    # bucket = bucket.list_folder('tuan-bucket-19', 'tuan99/tuan02')._info
    print(bucket)

def do_delete_object_all():
    bucket = init_bucket()
    bucket = bucket.delete_object_all('tuan-bucket-6', objs)._info
    print(bucket)

def do_delete_cors():
    bucket = init_bucket()
    bucket = bucket.delete_cors('tuan-bucket-20', 'ad243')._info
    print(bucket)


data = []
obj_cors = {
            # 'ID': 'ad243',
            'AllowedMethods': ['GET', 'POST'],
            'AllowedOrigins': ['58.186.85.243', '58.186.85.244'],
            'AllowedHeaders': ['*'],
            'MaxAgeSeconds': 2000
        }
data.append(obj_cors)


def do_set_cors():
    bucket = init_bucket()
    bucket = bucket.set_cors('tuan-bucket-20', obj_cors)._info
    print(bucket)


obj2 = {
                'ID': '246',
                'AllowedMethods': ['GET', 'PUT'],
                'AllowedOrigins': ['58.186.85.245', '58.186.85.246'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 20000
            }


def do_edit_cors():
    bucket = init_bucket()
    bucket = bucket.edit_cors('tuan-bucket-20', obj2)._info
    print(bucket)


def do_get_cors():
    bucket = init_bucket()
    bucket = bucket.get_cors('tuan-bucket-20')._info
    print(bucket)


def do_test_share_file():
    bucket = init_bucket()
    bucket = bucket.share_file('tuan-bucket-19', 'ram.jpg', 1000)._info
    print(bucket)


def do_permission_object():
    bucket = init_bucket()
    # bucket = bucket.permission_object('tuan-bucket-2', 'public-read', 'anh_size_ao.png')._info
    # bucket = bucket.permission_object('tuan-bucket-2', 'private', 'anh_size_ao.png')._info
    # bucket = bucket.permission_object('tuan-bucket-2', 'private')._info
    bucket = bucket.permission_object('tuan-bucket-2', 'public-read')._info
    print(bucket)

def do_test_constnts():
    print(CONF.ENDPOINT)
    print(CONF.STATIC_WEB)

def do_get_policy():
    bucket = init_bucket()
    bucket = bucket.get_policy('tuan-bucket-9')._info
    print(bucket)

def do_set_policy():
    bucket = init_bucket()
    bucket = bucket.set_policy('tuan-bucket-9', 'Allow')._info
    print(bucket)

def do_delete_policy():
    bucket = init_bucket()
    bucket = bucket.delete_policy('tuan-bucket-9')._info
    print(bucket)

def do_test_get_quota():
    bucket = init_bucket()
    bucket = bucket.get_quota()._info
    print(bucket)

# do_test_list_bucket()
# do_test_create_bucket()
# do_test_get_bucket()
# do_test_delete_bucket()
# do_test_create_folder()
# do_test_upload_file()
# do_test_download_file()
# do_test_put_objet()
# do_test_upload_file()
# do_list_versioning()
# do_delete_file_versioning()
# do_set_versioning()
# do_list_objects()
# do_list_folder()
# do_delete_object_all()
# do_delete_cors()
# do_set_cors()
# do_edit_cors()
# do_get_cors()
# do_test_share_file()
# do_permission_object()
# do_test_constnts()
# do_get_policy()
# do_set_policy()
# do_delete_policy()
do_test_get_quota()