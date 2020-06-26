from flask import render_template, flash, redirect, url_for

from app import app   #导入app对象


@app.route('/')
def index():
    user = {
        'username':'lizhao'
    }

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
    return render_template('index.html',user=user,title='home',posts=posts)

from app.forms import LoginForm
@app.route('/login',methods=['GET','POST'])
def login():

    loginform = LoginForm()

    if loginform.validate_on_submit():

        flash('Login requested for user {},remember_me={}'.format(loginform.username.data, loginform.remember_me.data))
        return redirect(url_for('index'))

    return render_template('login.html',form=loginform,title='Sign in')