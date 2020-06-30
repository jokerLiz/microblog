from datetime import datetime
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


'''
当用户登录后，每次进入某视图函数渲染返回的模板之前
都会调用该函数，用于加载用户信息
'''
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')       #反向引用，懒加载

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)      #时间

    #显示指定格式
    def __repr__(self):
        return '<User {}>'.format(self.username)

    #设置hash密码
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #验证hash密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #生成头像
    def avantar(self,size):
        hashvalue = md5(self.email.lower().encode('utf-8')).hexdigest()
        avantar_url =  f'https://s.gravatar.com/avatar/{hashvalue}?d=identicon&s={size}'
        return avantar_url

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}'.format(self.body)