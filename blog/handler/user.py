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
import datetime

# 用户相关的路由类实例化，后边需要在app.py中注册
user_router = MagWeb.Router(prefix='/user')


# 生成token
def gen_token(user_id):
    return jwt.encode({'user_id': user_id, 'timestamp': int(datetime.datetime.now().timestamp())},
                      key=config.AUTH_SECRET, algorithm='HS256').decode()


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
    payload = request.json
    print(payload)

    # 先检查登陆用户是否正确
    email = payload['email']
    user = session.query(User).filter(User.email == email).first()
    password_check = bcrypt.checkpw(payload['password'].encode(), user.password.encode())
    if user and password_check:  # 登陆用户与密码较验都通过时
        return jsonify(
            user={
                'id': user.id,
                'name': user.name,
                'email': user.email
            },
            tokeen=gen_token(user.id)
        )
    else:
        raise exc.HTTPUnauthorized()


# 用户是否已登陆状态的认证,判断条件： 1. jwt token中时间不过期 2. 数据库中能查出此用户
# 此装饰器由拦截器改造来
def authenticate(fn):
    def wrapper(ctx, request: MagWeb.Request):
        try:
            jwt_str = request.headers.get('jwt')  # token通过header传递，与业务数据分离
            payload = jwt.decode(jwt_str, key=config.AUTH_SECRET, algorithms=['HS256'])

            # 判断是否过期
            if (datetime.datetime.now().timestamp() - payload.get('timestamp', 0)) > config.AUTH_EXPIRE:
                raise exc.HTTPUnauthorized()

            # 判断用户是否存在
            user_id = payload.get('user_id', -1)
            user = session.query(User).filter(User.id == user_id).first()
            # payload.get('user_id', -1) payload中没有user_id那直接给-1，使数据库查询能进行
            if user is None:
                raise exc.HTTPUnauthorized()
            request.user = user  # 动态绑定一个属性
        except Exception as e:
            raise exc.HTTPUnauthorized()
        return fn(ctx, request)  # 不能放到try中，否则内层的异常会被改成了HTTPUnauthorized
    return wrapper






