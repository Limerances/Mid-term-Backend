### Mac 安装步骤

#### 环境安装

```shell
virtualenv env -p python
pip install Django
pip install django-cors-headers
pip install paramiko
pip install pycryptodome
```

#### 项目加载

在文件`backend/views.py`中修改`KEY_PATH`为公钥地址

运行

```shell
python manage.py runserver 0.0.0.0:55001
```

#### 值得关注的文件

`json`文件在`pageinfo`文件夹中