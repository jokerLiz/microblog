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


#关注者关联表
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),    #关注者
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))     #被关注者
    )

#User表
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')       #反向引用，懒加载

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)      #时间

    #声明多对多关系
    followed = db.relationship(                  #user.followed:查询该user关注了谁
        'User',          #另一个实体类
        secondary=followers,            #实体之间的关系的关联表
        primaryjoin=(followers.c.follower_id == id),       #主连接，在关联表中关联user表的id 与 关注者的id
        secondaryjoin=(followers.c.followed_id == id),     #次连接，在关联表中关联另一个user表的id 与 被关注者的id
        backref=db.backref('followers', lazy='dynamic'),         #反向引用，另一边的user可以通过user.followers查询它的粉丝
        lazy='dynamic'
    )


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

    #点关注
    def follow(self,user):
        #如果没有关注该用户，才能关注
        if not self.is_follow(user):
            self.followed.append(user)

    #取消关注
    def unfollow(self,user):
        # 如果关注了该用户，才能取消关注
        if self.is_follow(user):
            self.followed.remove(user)


    #是否关注
    def is_follow(self,user):

        #如果有该条关注记录
        if self.followed.filter(followers.c.followed_id == user.id).count() != 0:
            return True
        else:
            return False

    #该用户关注的人以及自己的贴子
    def followed_posts(self):

        '''
            连接Posts表和followers表，在Posts表中连接followed_id和Posts表中user_id的项，--也就是查找所有被关注的user的帖子
            在上一步的followers表的基础上，再过滤followed_id那些行上follower.id为该用户的项，--在所有被关注的user中找到有当前用户关注的user对象
        '''
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        #当自己关注自己时，也需要查询自己的贴子
        own = Post.query.filter_by(user_id=self.id)
        #连接两个查询，进行排序
        return followed.union(own).order_by(Post.timestamp.desc())

    #粉丝数
    def fans(self):
        return len(list(self.followers))

    #关注数
    def unfans(self):
        return len(list(self.followed))

#帖子
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}'.format(self.body)





# 查询用户1关注了谁
# select follower.username
# from user
# join followers on user.id = followers.follower_id
# join user as follower on follower.id = followers.followed_id
# where user.id = 1

# --查询用户4的粉丝有谁
# select follower.username
# from user
# join followers on user.id = followers.followed_id
# join user as follower on follower.id = followers.follower_id
# where user.id = 4