

def main():
    # print("A")
    # s3_path = 's3:::/'
    # # bucket = s3_path.split('/')[1].split('/')[0]
    # bucket = s3_path.split('/')[1]
    # if bucket is "":
    #     print("YES")
    # print(bucket)
    # # if "/" in s3_path:
    # #     print("YES")
    # # else:
    # #     print("NO")
    # keys = ["tuan06/tuan01/leesin.png",  "tuan06/tuan02/"]
    # for i in keys:
    #     print(i)

    class Student:
        marks = 88
        name = 'Sheeran'
    # person = Student()
    # name = getattr(person, 'name')
    # print(name)
    # marks = getattr(person, 'marks')
    # print(marks)
    # old = getattr(person, 'old', None)
    # print(old)

    res = {
        'code': 'obj.code',
        'message': 'obj.message',
        'data': 'obj.data',
        # 'total': obj.total
    }
    old = getattr(res, 'old', None)
    print(old)


if __name__ == '__main__':
    main()
