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
```

- 文章发布接口

```
http://127.0.0.1:9000/post/
POST:
{
	"title":"test title2",
	"content":"test content2...."
}
header中加上 jwt: 值
```


- 单个文章查询接口

```
http://127.0.0.1:9000/post/文章id号
GET
```

