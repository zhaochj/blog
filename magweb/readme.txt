from wsgiref.simple_server import make_server
from magweb import MagWeb, jsonify
import json


# 创建Router实例化
idx = MagWeb.Router()
py = MagWeb.Router('/python')

# 路由对象在app中注册
MagWeb.register(idx)
MagWeb.register(py)

# @idx.route('^/$', 'GET')   # index = idx.route('^/$', 'GET')(index)
@idx.get('^/$')
def index(ctx: MagWeb.Context, request: MagWeb.Request) -> MagWeb.Response:
    html = '<html>欢迎来到我的主页</html>'
    res = MagWeb.Response()
    res.status_code = 200
    res.charset = 'utf-8'
    res.body = html.encode()
    return res


# @py.post('/(\\d+)')
@py.post('/{student_id:int}')   # 测试路径 http://127.0.0.1:9999/python/76435
def python(ctx: MagWeb.Context, request: MagWeb.Request) -> MagWeb.Response:
    # print(request.vars)  # 打印绑定的分组信息
    # print(request.vars.student_id)
    html = '<html>欢迎来到我的Python主页</html>'
    res = MagWeb.Response()
    res.status_code = 200
    res.body = html.encode()
    return res


# 拦截器
@MagWeb.pre_interceptor_reg
def show_headers(ctx: MagWeb.Context, request: MagWeb.Request) -> MagWeb.Request:
    # ctx.app.XXX   # 可以访问Application中的数据
    # print(request.path)
    # print(request.user_agent)
    return request


# @Application.post_interceptor_reg
@py.post_interceptor_reg
def show_prefix(ctx: MagWeb.Context, request: MagWeb.Request, response: MagWeb.Response) -> MagWeb.Response:
    # print('~~~~~~prefix = {}'.format(ctx.router.prefix))  # 在注册为全局拦截器时会有异常
    return response


# json化拦截器
@py.post_interceptor_reg
def show_json(cts: MagWeb.Context, request, response: MagWeb.Response):
    body = response.body.decode()
    return jsonify(body=body)


if __name__ == '__main__':
    server = make_server('127.0.0.1', 9999, MagWeb())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()

