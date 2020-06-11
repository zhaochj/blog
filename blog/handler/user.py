# 提供路由配置
# 提供用户登陆
# 提供用户注册


from magweb import MagWeb
import json
from ..model import User, session
from webob import exc
import bcrypt
from ..util import jsonify
import jwt
from .. import config

# 用户相关的路由类实例化，后边需要在app.py中注册
user_router = MagWeb.Router(prefix='/user')


# 生成token
def gen_token(user_id):
    return jwt.encode({'user_id': user_id}, key=config.AUTH_SECRET, algorithm='HS256').decode()


# 用户注册绑定请求方法与url
@user_router.post('/reg')
def reg(ctx, request: MagWeb.Request) -> MagWeb.Response:
    # 用户端发送json格式
    # {
    #     "password": "abc",
    #     "name": "tom",
    #     "email": "tom@magedu.com"
    # }

    payload = request.json
    # 验证邮箱是否唯一
    email = payload.get('email')
    if session.query(User).filter(User.email == email).first() is not None:  # 在表中找到了email
        raise exc.HTTPConflict('{} already exists.'.format(email))

    # 如果在数据库中未找到email，则需要写入数据库中
    user = User()

    try:
        # 绑定字段属性
        user.name = payload.get('name')
        user.email = payload['email']  # email是必填字段，不使用get获取数据
        user.password = bcrypt.hashpw(payload['password'].encode(), bcrypt.gensalt())
        # password字段需要使用bcrypt处理
    except Exception as e:
        print(1, e)
        raise exc.HTTPBadRequest()

    session.add(user)

    try:
        session.commit()
        return jsonify(token=gen_token(user.id))
    except:
        session.rollback()
        raise exc.HTTPInternalServerError()


# 用户登陆绑定请求方法与url
@user_router.post('/login')
def login(ctx, request: MagWeb.Request) -> MagWeb.Response:
    print(request)
