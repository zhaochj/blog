from wsgiref.simple_server import make_server
from blog import config
from magweb import MagWeb
from blog.handler.user import user_router


if __name__ == '__main__':
    applications = MagWeb()

    # 用户注册，登陆相关的路由注册
    applications.register(user_router)

    server = make_server(config.WSIP, config.WSPORT, applications)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()



