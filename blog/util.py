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



