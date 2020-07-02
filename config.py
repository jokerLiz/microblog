import os

basedir = os.path.abspath(os.path.dirname(__file__))#获取当前.py文件的绝对路径

class Config():
    
    # DEBUG = True

    #环境变量中的SECRET_KEY的值/固定值
    #在teminal中设置环境变量---set SECRET_KEY=xxx
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess'

    #sqlite数据库文件的路径：环境变量中设定/当前路径下创建app.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    #关闭动态追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #设置每页的贴子数量
    POSTS_PER_PAGE = 2