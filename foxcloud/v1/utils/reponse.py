import json

class Response:

    # def __init__(self, code, message, data, total):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        # self.data = data
        # self.total = total

    # def response_model(self, obj):
    #     res = {
    #         'code': obj.code,
    #         'message': obj.message,
    #         # 'data': obj.data,
    #         # 'total': obj.total
    #     }
    #     # return json.dump(res)
    #     return res

    def to_dict(self, obj):
        result = dict()
        total = getattr(obj, 'total', None)
        data = getattr(obj, 'data', None)
        result['code'] = obj.code
        result['message'] = obj.message
        if data is not None:
            result['data'] = data
        if total is not None:
            result['total'] = total
        return result


