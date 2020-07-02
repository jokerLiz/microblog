from datetime import datetime
from hashlib import md5

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse

from app import app, db  # 导入app.db对象
from app.models import User, Post, followers

from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm


'''更新用户上一次登陆时间'''
@app.before_request
def before_request():

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

'''首页'''
@app.route('/',methods=['GET','POST'])
@login_required       #指定该函数需要登陆才能访问,否则函数中使用到的current_user为匿名用户，不能访问到内容
def index():
    # user = {
    #     'username':'lizhao'
    # }
    '''实例化表单类'''
    form = PostForm()
    #表单提交操作
    if form.validate_on_submit():
        #创建post对象，当前用户id，输入框内容
        post = Post(user_id=current_user.id,body=form.post.data)

        #提交数据库
        db.session.add(post)
        db.session.commit()
        #重定向到index
        return redirect(url_for('index'))

    #获取前台传来的页码，默认为1
    page = request.args.get('page', 1, type=int)

    # 获取用户以及该用户关注的人的贴子，并根据页码page分页
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)

    #如果posts对象有下一页，那么就再次访问index，并加上参数page，值为posts的下一个页码，否则传递None值。同理上一页
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html',
                           title='home',        #标题栏
                           posts=posts.items,         #贴子数据
                           form=form,           #表单对象
                           next_url=next_url,   #下一页的连接
                           prev_url=prev_url,   #上一页的连接
                           )



'''登录'''
@app.route('/login',methods=['GET','POST'])
def login():

    '''
    利用session判断当前是否是登录状态
    current_user：实质上首先调用models.py中的load_user()加载用户
    然后查看该用户是否已认证
    '''
    if current_user.is_authenticated:          #若为true，表示已登录，返回index页面
        return redirect(url_for('index'))

    #实例化表单
    loginform = LoginForm()

    if loginform.validate_on_submit():

        user = User.query.filter_by(username=loginform.username.data).first()

        if user is None or not user.check_password(loginform.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user,remember=loginform.remember_me.data)

        flash('Login requested for user {},remember_me={}'.format(loginform.username.data, loginform.remember_me.data))

        next_page = request.args.get('next')        #获取next的值

        if not next_page or url_parse(next_page).netloc != '':      #判断next_page的是否存在，以及是否合法(是否有http前缀，防止跳转到其他网站)
            next_page = url_for('index')           #如果不存在/不合法，将该值设为index
        return redirect(next_page)

    return render_template('login.html',form=loginform,title='Sign in')


# @app.route('/test')
# def test():
#
#     #转为hash密码
#     hash = generate_password_hash('123456')
#     print(hash)
#
#
#     #校验密码
#     print(check_password_hash(hash,'123456'))   #false
#     print(check_password_hash(hash,'654321'))   #true
#
#     return 'test'

'''注册'''
@app.route('/register',methods=['GET','POST'])
def register():

    if current_user.is_authenticated:

        return redirect(url_for('index'))
    form = RegistrationForm()

    if form.validate_on_submit():

        username = form.username.data      #获取form数据
        password = form.password.data
        email = form.password.data


        user = User(username=username,email=email)     #实例化user对象

        user.set_password(password)    #设置hash密码
        try:
            #提交数据库
            db.session.add(user)
            db.session.commit()
        except:
            return '数据库操作失败'

        flash('注册成功')

        return redirect(url_for('login'))

    return render_template('register.html',form=form,title='register')


'''退出'''
@app.route('/logout')
def logout():

    #退出当前用户
    logout_user()

    return redirect(url_for('index'))


# @app.route('/detail',methods=['GET'])
# def detail():
#     return render_template('detail.html',title='detail')
#
# @app.route('/detail',methods=['POST'])
# @login_required      #需要登录才能进入此函数
# def post_comment():
#     return 'saasa'


'''用户个人中心'''
@app.route('/user/<username>')
@login_required
def user(username):
    #查询该用户对象
    user = User.query.filter_by(username=username).first_or_404()

    # 获取前台传来的页码，默认为1
    page = request.args.get('page', 1, type=int)

    #user.posts:通过对应关系，获取该用户所有的贴子
    # 获取当前对象的的所有贴子，排序,并根据page分页
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)

    # 如果posts对象有下一页，那么就再次访问，并加上参数page，值为posts的下一个页码，否则传递None值。同理上一页
    next_url = url_for('user', username=current_user.username,page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=current_user.username,page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html',
                           user=user,
                           posts=posts.items,
                           title='user',
                           next_url=next_url,
                           prev_url=prev_url,
                           )


# @app.route('/avantar')
# def avantar():
#     hashvalue = md5(b'dsadwdde').hexdigest()
#     return hashvalue


'''编辑个人资料'''
@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():

    #实例化表单，把username传进去
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():

       current_user.username = form.username.data
       current_user.about_me = form.about_me.data
       db.session.commit()

       flash('Your changes have been saved.')

       return redirect(url_for('user',username=current_user.username,title='user'))      #重定向到当前用户的详情页

    form.username.data = current_user.username
    form.about_me.data = current_user.about_me

    return render_template('edit_profile.html',form=form,title='edit_profile')


@app.route('/test')
def test():

    user1 = User.query.get(1)
    user2 = User.query.get(2)

    user1.follow(user2)       #user1 关注 user2

    db.session.commit()
    # print(list(user1.followed))    #[user2]
    # print(list(user1.followers))   #[]
    # print(list(user2.followed))    #[]
    # print(list(user2.followers))   #[user1]
    return 'yes'


'''用户关注'''
@app.route('/follow/<username>')
def follow(username):
    #查询当前要关注的用户
    user =User.query.filter_by(username=username).first()

    current_user.follow(user)      #执行点关注函数，在该函数中进行判断之前是否已经关注

    db.session.commit()

    return redirect(f'/user/{user.username}')

'''用户取消关注'''
@app.route('/unfollow/<username>')
def unfollow(username):
    #查询当前要取消关注的用户
    user =User.query.filter_by(username=username).first()

    current_user.unfollow(user)      #执行取消关注函数，在该函数中进行判断之前是否已经关注

    db.session.commit()

    return redirect(f'/user/{user.username}')



'''
开阔版首页
index只能展示与该用户相关的贴子，
explore展示所有用户的贴子
'''
@app.route('/explore')
def explore():

    #获取前台传来的页码，默认为1
    page = request.args.get('page', 1, type=int)

    #查询所有的贴子，并倒叙排序，并根据页码page分页
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)

    #如果posts对象有下一页，那么就再次访问explore，并加上参数page，值为posts的下一个页码，否则传递None值。同理上一页
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    #返回index页面，但是数据填充不同
    return render_template('index.html',
                           posts=posts.items,
                           title='explore',
                           next_url=next_url,
                           prev_url=prev_url
                           )
