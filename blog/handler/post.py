from magweb import MagWeb
from .user import authenticate
from ..model import session, Post, Content
from webob import exc
from ..util import jsonify, validate
import datetime


# 与文章的路由
post_router = MagWeb.Router(prefix='/post')


# 文章发布接口 /post/

@post_router.post('/')  # pub = post_router.post('/')(pub)
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
            'postdate': post.postdate.timestamp(),
            # 需要转换为timestamp，否则报Object of type 'datetime' is not JSON serializable
            'content': post.content.content
        })
    except Exception as e:
        print(e)
        raise exc.HTTPNotFound()


# 文章列表页显示
@post_router.get('/')
def article_list(ctx, request: MagWeb.Request):
    # http://url/post?page=2
    # page值获取
    # try:
    #     page = int(request.params.get('page', 1))  # 从request中获取params，无法获取就默认是第一页
    #     page = page if page > 0 else 1
    # except:
    #     page = 1

    page = validate(request.params, 'page', 1, int, lambda x, y: x if x > 0 else y)  # 对page和size值的获取，在逻辑上发现有些相似，所以可以抽象成一个函数来操作

    # 每页显示多少条数据，这个值可以在浏览器端提供给用户选择，但要做好范围的控制，也可不提供
    # try:
    #     size = int(request.params.get('size', 10))
    #     size = size if 0 < size < 101 else 20
    # except:
    #     size = 20

    size = validate(request.params, 'size', 10, int, lambda x, y: x if 0 < x < 101 else y)

    try:
        # 数据为操作，获取数据，返回
        posts = session.query(Post).order_by(Post.id.desc()).limit(size).offset(size * (page - 1)).all()
        return jsonify(posts=[{'post_id': post.id, 'title': post.title, 'postdate': post.postdate.timestamp()} for post in posts])
    except Exception as e:
        print(e)
        raise exc.HTTPInternalServerError()
