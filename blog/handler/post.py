from magweb import MagWeb
from .user import authenticate
from ..model import session, Post, Content, Dig, Tag, Post_tag
from webob import exc
from ..util import jsonify, validate
import datetime
import math
import re

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

        tags = payload.get('tags')  # 获取标签，来源： 标签1\t\n标签2,标签3\n标签4
    except Exception as e:
        # print(2, e)
        raise exc.HTTPBadRequest()

    # 处理标签，切分标签，组装字段
    tag_list = re.split(r'[\s,+]', tags)
    for tag in tag_list:
        t = session.query(Tag).filter(Tag.tag == tag).first()
        if not t:  # 标签在数据库中未找到时，需要组装字段，准备写数据库
            t = Tag()
            t.tag = tag
            session.add(t)  # 标签数据准备好

        # 页面上传来标签，先判断这个标签在数据库中是否存在，如果不存在，就准备把标签插入到tag表中，插入后就有标签的id号。如果存在就不做对tag表的处理
        # 接下来需要操作post_tag这个中间表，不管标签是否存在，现在都有了t这个实例，即一行关于这个标签的数据，post_tag中post_id与tag_id这两个字段分别外键关联了
        # post表中的id和tag表中id，所以不需要单独为这两个字段赋值，而是应该去找关联表中的相应的值，所以在post_tag中定义了两个relationship关系，通过这个关系就
        # 可以找到相应的值。所以才有下边的"pt.tag = t"和“pt.post = post”这种写法，这样就可以自动在"t"和"post"这两个实例上去找相应的外键所需要的值。这种写法很独特
        pt = Post_tag()
        pt.tag = t   # model中 tag = relationship('Tag') 定义了这个关系。
        pt.post = post  # model中 post = relationship('Post') 定义了这个关系
        session.add(pt)

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

        # 处理标签数据，把文章的id在post_tag表中进行查找
        pts = session.query(Post_tag).filter(Post_tag.post_id == p_id).limit(10).all()  # 进行limit的目的是当文章标签很多时，只显示几个
        # 需要返回什么数据？标签名称，标签id
        tags = [[x.tag.id, x.tag.tag] for x in pts]  # 准备一个数组返回，通过表中的relationship获取tag表中的数据

        bury_info, dig_info = get_digs(p_id)

        return jsonify(post={
            'post_id': post.id,
            'title': post.title,
            'author': post.author.name,
            'author_id': post.author_id,
            'postdate': post.postdate.timestamp(),
            # 需要转换为timestamp，否则报Object of type 'datetime' is not JSON serializable
            'content': post.content.content
        }, diginfo=dig_info, buryinfo=bury_info, tags=tags)
    except Exception as e:
        print(e)
        raise exc.HTTPNotFound()


@post_router.get('/')  # 所有文章列表页显示
@post_router.get('/u/{id:int}')  # 某个用户文章列表显示
@post_router.get('/t/{tag:str}')  # 按标签来列表显示
def article_list(ctx, request: MagWeb.Request):
    # 对page和size值的获取，在逻辑上发现有些相似，所以可以抽象成一个函数来操作
    page = validate(request.params, 'page', 1, int, lambda x, y: x if x > 0 else y)
    # 每页显示多少条数据，这个值可以在浏览器端提供给用户选择，但要做好范围的控制，也可不提供
    size = validate(request.params, 'size', 10, int, lambda x, y: x if 0 < x < 101 else y)

    # 按某个用户文章列表显示处理
    # request.vars.id  这个值是我们的web框架绑定的属性，不是字典，用户未按要求传递，此值可能获取不到
    query = session.query(Post)
    try:
        user_id = validate({'id': request.vars.id}, 'id', -1, int, lambda x, y: x if x > 0 else y)
    except:
        user_id = -1  # 获取id出错就给个 -1 ，因此值在数据库中一定不存在
    if user_id > 0:  # 如果有合法的user_id，则增加过滤条件
        query = query.filter(Post.author_id == user_id)

    # 按标签来列表显示
    try:
        tag_name = validate({'tag': request.vars.tag}, 'tag', '', str, lambda x, y: x if len(x) else y)
    except:
        tag_name = ''
    if tag_name:
        query = query.join(Post_tag, Post.id == Post_tag.post_id).join(Tag, Post_tag.tag_id == Tag.id).filter(tag_name == Tag.tag)  # 三表联合查询找到标签的名称

    try:
        # 数据操作，获取数据，返回
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
