from wsgiref.simple_server import make_server
from blog import config
from magweb import MagWeb


if __name__ == '__main__':
    applications = MagWeb()
    server = make_server(config.WSIP, config.WSPORT, applications)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()



