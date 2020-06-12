from magweb import MagWeb
from .user import authenticate
from ..model import session, Post, Content
from webob import exc
from ..util import jsonify
import datetime


# 与文章的路由
post_router = MagWeb.Router(prefix='/post')


# 文章发布接口 /post/

@post_router.post('/')   # pub = post_router.post('/')(pub)
@authenticate  # 验证
def pub(ctx, request: MagWeb.Request):
    # 用户要发布文章： 1. 需要登陆，需要验证用户， 2. 需要title, content
    try:
        payload = request.json
    except Exception as e:
        raise exc.HTTPBadRequest('数据解析出错')
    post = Post()
    try:
        post.title = payload.get('title')
        post.author_id = request.user.id  # 通过@authenticate验证后会在request上绑定user实例
        post.postdate = datetime.datetime.now()

        # content实际存放在Content实体对象中，需要使用以下方式绑定数据
        _content = Content()
        _content.content = payload['content']
        post.content = _content
    except Exception as e:
        print(2, e)
        raise exc.HTTPBadRequest()

    session.add(post)
    try:
        session.commit()
        return jsonify(post_id=post.id)
    except:
        session.rollback()
        raise exc.HTTPInternalServerError()


# 查看单个博文
@post_router.get('/{id:int}')
def get(ctx, request: MagWeb.Request) -> MagWeb.Response:
    p_id = request.vars.id
    try:
        post = session.query(Post).get(p_id)  # 可以使用下边语句
        # post = session.query(Post).filter(Post.id == p_id).first()
        return jsonify(post={
            'post_id': post.id,
            'title': post.title,
            'author': post.author.name,
            'author_id': post.author_id,
            'postdate': post.postdate.timestamp(),  # 需要转换为timestamp，否则报Object of type 'datetime' is not JSON serializable
            'content': post.content.content
        })
    except Exception as e:
        print(e)
        raise exc.HTTPNotFound()







