import webob
import re
from webob.exc import HTTPNotFound
from webob import dec
import json


class Dict2Obj:
    # 字典属性化
    def __init__(self, d: dict):
        if isinstance(d, (dict,)):
            self.__dict__['_dict'] = d
        else:
            self.__dict__['_dict'] = {}

    def __getattr__(self, item):
        try:
            return self.__dict__['_dict'][item]
        except KeyError:
            raise AttributeError('Attribute {} Not Found'.format(item))

    def __setattr__(self, key, value):
        raise NotImplementedError

    def __str__(self):
        return str(self.__dict__['_dict'])


class Context(dict):   # 继承自内建dict对象
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('Attribute {} Not Found'.format(item))

    def __setattr__(self, key, value):
        self[key] = value


class NestedContext(Context):  # 一个嵌套的上下文管理类，继承自Context
    # 上下文管理类，实现一个类的实例对象查找属性时先查找自己实例中的属性，如果没有去全局的实例的属性查找
    # 查询一个属性形成了一个层次查找，类似类继承一样，先找自己实例的的，再找类的，再找父类的，直到找到为止或找不到出异常
    def __init__(self, global_context: Context = None):
        super().__init__()
        self.relate(global_context)

    def relate(self, global_context: Context = None):
        # global_context实例对象与当前类实例建立关系
        self.global_context = global_context

    def __getattr__(self, item):
        # 方法一
        # try:
        #     return self[item]  # 先找本实例对象
        # except KeyError:
        #     return self.global_context[item]  # 再找上一级的

        # 方法二
        if item in self.keys():
            return self[item]
        return self.global_context[item]


class _Router:
    """
    实现URL路由
    """
    # 类型对应的正则模式
    TYPE_PATTERN = {
        'str': r'[^/]+',
        'word': r'\w+',
        'int': r'[+-]?\d+',
        'float': r'[+-]?\d+\.\d+',
        'any': r'.+'
    }

    # 字符串与之类型的映射
    TYPECAST = {
        'int': int,
        'str': str,
        'float': float,
        'word': str,
        'any': str
    }

    regx = re.compile('/({[^{}:]+:?[^{}:]*})')  # 放在类属性中的优点：此pattern是通用的，用不着每个实例都定义，可以加速

    def __init__(self, prefix: str = ''):
        self.__prefix = prefix.rstrip('/')
        self.__router_table = []  # 存放四元组 [(re.compile(pattern), {'name': str, 'id': int}, ('GET', 'POSt'), index),(......)]
        # 路由阶段的拦截器
        self.pre_interceptor = []
        self.post_interceptor = []
        # 上下文对象
        self.ctx = NestedContext()  # 未关联全局，注册时注入

    # 路由阶段拦截器注册装饰器
    def pre_interceptor_reg(self, fn):
        self.pre_interceptor.append(fn)
        return fn

    def post_interceptor_reg(self, fn):
        self.post_interceptor.append(fn)
        return fn

    def _parse(self, src: str):
        # '/python/{name:str}/{id:int}'  转换为  '/python/(?P<name>[^/]+)/(?P<id>[+-]?\d+)'
        start = 0
        result = ''
        translator = {}  # 记录用户定义时名称与类型的对应关系   {name: str, id: int}
        while True:
            matcher = self.regx.search(src, start)
            if matcher:
                result += src[start:matcher.start()]  # prefix部分：/python
                # '/{name:str}
                strings = matcher.group()
                name, _, name_type = strings.strip('/{}').partition(':')  # 解构
                result += '/(?P<{}>{})'.format(name.strip(), self.TYPE_PATTERN.get(name_type.strip(), r'\w+'))  # 拼接
                translator[name] = self.TYPECAST.get(name_type.strip(), str)  # 记录名称与类型的映射
                start = matcher.end()  # 移动匹配的起点
            else:
                break
        if result:  # 有匹配后进行了相应的转换
            return result, translator
        else:  # 没有一次进行转换， 如： '/student/xxx/12356'
            return src, translator

    def route(self, user_pattern, *methods):
        # 增加路径装饰器，如果不传入method，那约定允许所有的方法都将调用相应的handler
        def wrapper(handler):
            # pattern要做转换后才加入？？？？
            pattern, name_type = self._parse(user_pattern)  # 转换函数
            self.__router_table.append((re.compile(pattern), name_type, methods, handler))  # patter在这里进行编译
            return handler
        return wrapper

    @property
    def prefix(self):  # 提供一个属性方法，便于查询
        return self.__prefix

    def get(self, pattern):
        # GET方法装饰器
        return self.route(pattern, 'GET')

    def post(self, pattern):
        # POST方法装饰器
        return self.route(pattern, 'POST')

    def head(self, pattern):
        # HEAD方法装饰器
        return self.route(pattern, 'HEAD')

    def matcher(self, request: webob.Request) -> webob.Response:
        if not request.path.startswith(self.__prefix):  # path的前缀不匹配直接返回None
            return None

        # 拦截请求
        for fn in self.pre_interceptor:
            request = fn(self.ctx, request)

        # 在保证前缀后，做正则匹配
        for pattern, name_type, methods, handler in self.__router_table:
            if not methods or request.method.upper() in methods:  # not methods表示一个方法都没有定义，则支持全部方法
                matcher = pattern.match(request.path.replace(self.__prefix, '', 1))  # 去掉前缀后进行match
                if matcher:
                    # 在request对象上绑定分组信息
                    # request.args = matcher.groups()

                    # matcher.groupdict() 这个字典是正则匹配到分组后把分组名称与之对应的模式匹配到的字符的映射，类型都是str，需要对匹配到分组的数据进行类型转换
                    new_dict = {}
                    for k, v in matcher.groupdict().items():
                        new_dict[k] = name_type[k](v)  # 进行类型转换
                    request.vars = Dict2Obj(new_dict)  # 字典属性化后动态绑定到request对象，最后传递到相应的handler
                    # print(new_dict)
                    response = handler(self.ctx, request)  # 增加上下文参数，并回传request，相应的handler就可以拿到分组信息

                    # 拦截响应
                    for fn in self.post_interceptor:
                        response = fn(self.ctx, request, response)
                    return response
        # self.__router_table一个都没有匹配时 return None


class MagWeb:
    # 类属性方式把类暴露出去
    Router = _Router
    Context = Context
    Request = webob.Request
    Response = webob.Response

    ROUTERS = []  # Router实例列表
    ctx = Context()  # 全局上下文对象，用于存放一些全局共享信息，信息来源可以是实例化传递进来，也可以是加载配置文件后解析得来

    # 拦截器存放，执行时顺序执行
    PRE_INTERCEPTOR = []
    POST_INTERCEPTOR = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.ctx[k] = v
        self.ctx.app = self  # 在ctx这个类属性上绑定一个app对象，对象指向Application实例，这样的目的是便于在想调用Application中的数据时直接使用ctx.app即可

    @classmethod
    def register(cls, router: Router):
        # 为router实例注入全局上下文
        router.ctx.relate(cls.ctx)
        router.ctx.router = router  # 动态绑定属性
        cls.ROUTERS.append(router)

    # 全局拦截器函数注册装饰器
    @classmethod
    def pre_interceptor_reg(cls, fn):
        cls.PRE_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def post_interceptor_reg(cls, fn):
        cls.POST_INTERCEPTOR.append(fn)
        return fn

    @dec.wsgify
    def __call__(self, request: webob.Request) -> webob.Response:
        # 当有请求进来时，遍历ROUTERS,调用Router实例的matcher方法，看谁匹配

        # 全局拦截请求数据
        for fn in self.PRE_INTERCEPTOR:
            request = fn(self.ctx, request)   # 这里传递self.ctx 似乎是有问题的？？？因Contex是NestedContex的父类

        # 遍历ROUTERS，调用Router实例的matcher方法，看谁匹配
        for router in self.ROUTERS:
            response = router.matcher(request)

            # 全局拦截响应数据
            for fn in self.POST_INTERCEPTOR:
                # 这里传递self.ctx 似乎是有问题的？？？因Contex是NestedContex的父类
                response = fn(self.ctx, request, response)  # response重新赋值，前一个拦截函数的输出作为下一次拦截函数的输入

            # print(self.POST_INTERCEPTOR)
            if response:  # 返回None或response对象
                return response
        raise HTTPNotFound('你访问的页面不存在！')


# 数据json化函数
def jsonify(**kwargs):
    content = json.dumps(kwargs)
    return MagWeb.Response(body=content, status='200 ok', content_type='application/json', charset='utf-8')

