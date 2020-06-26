from flask import Flask
from config import Config


#创建app对象,             设置templates模板文件的相对于本文件的位置
app = Flask(__name__)


app.config.from_object(Config)         #关联配置文件

from app import routes      #导入该对象的路由和视图函数
