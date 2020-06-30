from datetime import datetime
from hashlib import md5

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse

from app import app, db  # 导入app.db对象
from app.models import User

from app.forms import LoginForm, RegistrationForm, EditProfileForm


#上一次登陆时间
@app.before_request
def before_request():

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
# @login_required       #指定该函数需要登陆才能访问
def index():
    # user = {
    #     'username':'lizhao'
    # }

    posts = [
        # 创建一个列表：帖子。里面元素是两个字典，每个字典里元素还是字典，分别作者、帖子内容。
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',title='home',posts=posts)




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


@app.route('/logout')
def logout():

    #退出当前用户
    logout_user()

    return redirect(url_for('index'))

@app.route('/detail',methods=['GET'])
def detail():
    return render_template('detail.html',title='detail')

@app.route('/detail',methods=['POST'])
@login_required      #需要登录才能进入此函数
def post_comment():
    return 'saasa'

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',user=user,posts=posts,title='user' )


# @app.route('/avantar')
# def avantar():
#     hashvalue = md5(b'dsadwdde').hexdigest()
#     return hashvalue

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