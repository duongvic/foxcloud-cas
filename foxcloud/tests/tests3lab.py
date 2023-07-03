# -*- coding: utf-8 -*-
# encoding=utf8
import boto3
import math


def check_disk_space(used, total):
    try:
        percent = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    return round(percent, 1)

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def main():
    print("tuantd")
    s3 = boto3.client('s3',
                      endpoint_url='http://ss.fptcompute.com.vn',
                      aws_access_key_id='tuantdpw',
                      aws_secret_access_key='6SmJXpOgWgB6Wyoh9zqT77sN8ZnNfvqUgjA3sx9M', verify=False)

    s3res = boto3.resource('s3',
                           endpoint_url='http://ss.fptcompute.com.vn',
                           aws_access_key_id='tuantdpw',
                           aws_secret_access_key='6SmJXpOgWgB6Wyoh9zqT77sN8ZnNfvqUgjA3sx9M', verify=False)
    # sys.setdefaultencoding('utf8')

    # get list bucket, total objs, total size
    total_sizes = []
    total_objs = []
    for bucket in s3res.buckets.all():
        bucket_name = bucket.name

        total_size = 0
        count_obj = 0
        bucket = s3res.Bucket(bucket_name)
        for k in bucket.objects.all():
            total_size += k.size
            count_obj += 1
        # print(total_size)
        # print(count_obj)
        total_sizes.append(total_size)
        total_objs.append(count_obj)
        # print(total_sizes)
        # print(total_objs)

    sum_sizes = sum(total_sizes, 0)
    sum_objs = sum(total_objs, 0)
    print(sum_sizes)
    print(sum_objs)
    print(convert_size(sum_sizes))
    print(convert_size(10000000000000)) # 9TB
    disk_space = check_disk_space(5015257, 10000000)
    # msg = ''
    if disk_space < 80:
        msg = 'AVAILABLE'
    else:
        msg = 'WARNING'
    print(msg)


if __name__ == '__main__':
    main()
