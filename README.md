# 博客开发实践！

## 各接口测试方法

- 注册接口

```
http://127.0.0.1:9000/user/reg   

POST:
{
	"password":"abc2",
	"name":"tom2",
	"email":"tom2@magedu.com"
}
```

- 登陆接口

```
http://127.0.0.1:9000/user/login
POST:
{
	"password":"abc2",
	"name":"tom2",
	"email":"tom2@magedu.com"
}
返回一个token
```

- 文章发布接口

```
http://127.0.0.1:9000/post/
POST:
{
	"title":"test title2",
	"content":"test content2....",
    "tags":"mysql 主从"
}
header中加上 jwt: 值
```


- 单个文章查询接口

```
http://127.0.0.1:9000/post/文章id号
GET
```

- 文章列表查询接口

```
http://127.0.0.1:9000/post/
GET
```

- 以某个用户列表显示文章

```
http://127.0.0.1:9000/post/u/用户id
GET
```

- 以某个标签来列表显示文章

```
http://127.0.0.1:9000/post/t/标签     路径中传递中文时请不要使用Postman测试，postman在路径中不能传递中文
GET
```

- 赞文章接口

```
http://127.0.0.1:9000/post/dig/3   --最后的3是post.id
PUT方法
加上jwt的token
```

- 踩文章接口

```
http://127.0.0.1:9000/burry/dig/3   --最后的3是post.id
PUT方法
加上jwt的token
```


