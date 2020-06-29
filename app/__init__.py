from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

#创建app对象,             设置templates模板文件的相对于本文件的位置
app = Flask(__name__)


app.config.from_object(Config)         #关联配置文件

db = SQLAlchemy(app)      #关联数据库对象

migrate = Migrate(app,db)        #数据迁移引擎对象

login = LoginManager(app)     #关联app对象
login.login_view = 'login'      #指定登录的视图函数名

from app import routes,models      #导入该对象的路由和视图函数，模型类
