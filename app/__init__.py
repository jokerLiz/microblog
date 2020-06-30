import logging
import os
from logging.handlers import RotatingFileHandler

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


if not app.debug:
    # ...

    if not os.path.exists('logs'):         #如果该目录中没有logs目录，就创建logs目录
        os.mkdir('logs')

    #在logs目录中生成日志文件，日志文件大小限制为10kb，并且将最后10个日志文件保留为备份。
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    #设置日志的格式 --- 时间戳、日志记录级别、消息、日志来源的源代码文件、行号
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    #设置日志记录级别降低到INFO，它们分别是DEBUG、INFO、WARNING、ERROR、CRITICAL（按严重程度递增）
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)     #加入file_handler



from app import routes,models,error      #导入视图函数以及model
