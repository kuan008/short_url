# short_url

一个基于Flask+Mongodb实现的极简短链接生成服务

**造轮子过程：**

##### 1.基础准备

安装mongodb，因为要用这个文档型数据库存储数据

[造轮子系列（1）--自己重写（抄）一个python的shortid生成工具](https://zhuanlan.zhihu.com/p/36172141)

文后github地址，clone下来后python setup.py install安装shortid依赖包，或者直接用文内提到的大佬实现的python包。


安装flask，我是直接用pycharm新建flask项目的。
安装flask-pymongo


##### 2.业务逻辑分析


![生成短链接逻辑](https://pic1.zhimg.com/80/v2-96933113ab97ce8f9240d8c89cdbcd74_hd.jpg)

![打开短链接的逻辑](https://pic2.zhimg.com/80/v2-eed128c2b21cfd59ccdf557384d7bff8_hd.jpg)

##### 3.开始撸代码

清楚简单的原理就可以开始实现这个简单的业务逻辑了

在app.py里写下这些导入这些依赖的代码
```
from flask import Flask,request, jsonify, url_for, redirect, abort
from flask_pymongo import PyMongo
import shortid
```

创建app实例并按默认配置初始化pymongo实例（本地27017端口无密码，数据库名为app名）
```
app = Flask(__name__)
mongodb = PyMongo(app)
```


写一个生成短链接的函数
```python
@app.route('/gen', methods=['POST'])
def generate_short():
    url = request.values.get('url')
    record = mongodb.db.short_urls.find_one({'url': url})
    if not record:
        record = {
            '_id': shortid.generate(),
            'url': url
        }
        mongodb.db.short_urls.insert_one(record)
    return jsonify(url_for('jump', short_id=record['_id'], _external=True))
```


限制post方式提交，通过
```python
request.values.get('url')
```

获取参数名为url的参数，也就是客户端提交过来的需要缩短的链接
```python
record = mongodb.db.short_urls.find_one({'url': url})
```

根据url在数据库里查询是否存在记录
如果不存在就新增一条，最后直接返回记录里的'id'，其中新增的时候定义的'_id'字段是调用了shortid生成的短id，虽然长度可能比世面上普通的短链接服务长1到2位，但也够用，或者可以自己写一个自增短id的实现方案，大概思路就是整型id自增，再将这个id转为62进制的字符串作为短id。

做完这些工作发现没做参数校验，有可能随便一个参数都会往数据库里写，导致可能出现一堆垃圾数据，找了个验证url的正则表达式加了个参数验证：改完之后如下：
```python
def validate_url(url):
    regex = re.compile('^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$', re.IGNORECASE)
    return regex.match(url)


@app.route('/gen', methods=['POST'])
def generate_short():
    url = request.values.get('url')
    if not validate_url(url):
        abort(500)
    record = mongodb.db.short_urls.find_one({'url': url})
    if not record:
        record = {
            '_id': shortid.generate(),
            'url': url
        }
        mongodb.db.short_urls.insert_one(record)
    return jsonify(url_for('jump', short_id=record['_id'], _external=True))
```

返回的数据用到了**url_for**函数，这个函数会根据传入的参数生成能访问到对应函数的url。

接下来实现访问短链接的函数：
```python
@app.route('/<string:short_id>')
def jump(short_id):
    record = mongodb.db.short_urls.find_one_or_404({'_id': short_id})
    return redirect(record['url'])

```

这里用到了flask-pymongo的一个扩展函数 find_one_or_404，如果数据不存在就直接返回404错误，否则
```python
return redirect(record['url'])
```

重定向到对应的url。

基础的服务到这就写完了，后来花了点时间从网上找了个模板，写了几行js代码完成了生成接口的调用，效果大概是下面这样：

![效果图](https://pic4.zhimg.com/80/v2-9a479e92b00151a6a1b3dcc2b6e4b475_hd.jpg)


最后的代码是超过了10行，不过差距也不大，业务核心代码差不多也就10行


预计扩展功能：短链管理、短链点击统计、短链密码限制等。