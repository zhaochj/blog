from magweb import MagWeb
from .user import authenticate
from ..model import session, Post, Content, Dig
from webob import exc
from ..util import jsonify, validate
import datetime
import math

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


def get_digs(p_id):
    # 赞踩总数
    dig_query = session.query(Dig).filter(Dig.post_id == p_id).filter(Dig.state == 1)
    dig_count = dig_query.count()
    dig_list = dig_query.order_by(Dig.pubdate.desc()).limit(10).all()  # 倒排序显示top10

    bury_query = session.query(Dig).filter(Dig.post_id == p_id).filter(Dig.state == 0)
    bury_count = bury_query.count()
    bury_list = bury_query.order_by(Dig.pubdate.desc()).limit(10).all()  # 倒排序显示top10

    # 需要在页面上显示最后10名赞，踩的用户id，用户名称(昵称)，这样前端就可以显示用户我头像。但目前dig表中有用户id，但没有用户名，所以需要在model.py中创建关系
    # 准备需要返回的数据，赞踩总数及top10用户信息
    dig_info = {'count': dig_count, 'digs': [{'id': x.user_id, 'name': x.user.name} for x in dig_list]}
    bury_info = {'count': dig_count, 'buries': [{'id': x.user_id, 'name': x.user.name} for x in bury_list]}
    return bury_info, dig_info


# 查看单个博文
@post_router.get('/{id:int}')
def get(ctx, request: MagWeb.Request) -> MagWeb.Response:
    p_id = request.vars.id
    try:
        post = session.query(Post).get(p_id)  # 可以使用下边语句
        # post = session.query(Post).filter(Post.id == p_id).first()

        # 调用此函数点击量加1
        post.hits += 1
        session.add(post)
        try:
            session.commit()
        except:
            session.rollback()

        bury_info, dig_info = get_digs(p_id)

        return jsonify(post={
            'post_id': post.id,
            'title': post.title,
            'author': post.author.name,
            'author_id': post.author_id,
            'postdate': post.postdate.timestamp(),
            # 需要转换为timestamp，否则报Object of type 'datetime' is not JSON serializable
            'content': post.content.content
        }, diginfo=dig_info, buryinfo=bury_info)
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

    page = validate(request.params, 'page', 1, int,
                    lambda x, y: x if x > 0 else y)  # 对page和size值的获取，在逻辑上发现有些相似，所以可以抽象成一个函数来操作

    # 每页显示多少条数据，这个值可以在浏览器端提供给用户选择，但要做好范围的控制，也可不提供
    # try:
    #     size = int(request.params.get('size', 10))
    #     size = size if 0 < size < 101 else 20
    # except:
    #     size = 20

    size = validate(request.params, 'size', 10, int, lambda x, y: x if 0 < x < 101 else y)

    try:
        # 数据为操作，获取数据，返回
        query = session.query(Post)
        count = query.count()  # 数据总数
        posts = query.order_by(Post.id.desc()).limit(size).offset(size * (page - 1)).all()
        return jsonify(
            posts=[{'post_id': post.id, 'title': post.title, 'postdate': post.postdate.timestamp()} for post in posts],
            pagination={
                'page': page,  # 第几页
                'size': size,  # 本页显示的数据条数
                'count': count,  # 所有数据的总条数
                'page_count': math.ceil(count / size)  # 页总数，向上取整
            })
    except Exception as e:
        print(e)
        raise exc.HTTPInternalServerError()


# 赞，踩函数
def dig_or_bury(state, user_id, post_id):
    _dig = Dig()
    _dig.user_id = user_id
    _dig.post_id = post_id
    _dig.state = state  # 状态，1表示赞, 0表示踩
    _dig.pubdate = datetime.datetime.now()

    session.add(_dig)
    try:
        session.commit()
        return jsonify(200)  # 成功返回200即可
    except:
        session.rollback()
        return jsonify(500)  # 赞，踩功能不是必要功能，即使写数据库有问题也不应该raise


@post_router.put('/dig/{id:int}')
@authenticate
def dig(ctx, request: MagWeb.Request):
    return dig_or_bury(1, request.user.id, request.vars.id)


@post_router.put('/bury/{id:int}')
@authenticate
def bury(ctx, request: MagWeb.Request):
    return dig_or_bury(0, request.user.id, request.vars.id)
