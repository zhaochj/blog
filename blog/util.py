# 工具模块

import json
from magweb import MagWeb


def jsonify(status=200, **kwargs):
    content = json.dumps(kwargs)

    res = MagWeb.Response()
    res.content_type = 'application/json'
    res.charset = 'UTF-8'
    res.status_code = status
    res.body = '{}'.format(content).encode('utf-8')
    return res


# 文章列表显示时对页面数据进行较验证函数
def validate(d: dict, name: str, default, converter_func, validate_fun):
    try:
        result = converter_func(d.get(name, default))
        result = validate_fun(result, default)
        return result
    except:
        return default


