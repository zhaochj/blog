# 工具模块

import json
from magweb import MagWeb


def jsonify(status=200, **kwargs):
    content = json.dumps(kwargs)
    response = MagWeb.Response()
    response.content_type = 'application/json'
    response.charset = 'UTF-8'
    response.status_code = status
    response.body = '{}'.format(content).encode('utf-8')
    return response



