import os
class Config():
    DEBUG = True
    #环境变量中的SECRET_KEY的值/固定值
    #在teminal中设置环境变量---set SECRET_KEY=xxx
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess'