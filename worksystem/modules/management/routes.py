from . import management
from flask import render_template
from worksystem import login_manager

@management.route('/')
@management.route('/index')
def index():
    print('用户管理页面')
    login_manager.login_message = u'请先登录'
    return render_template('management/index.html',title='主页')

@management.route('/roles')
def roles():
    return render_template('management/roles.html',title='角色管理')

@management.route('/post')
def post():
    return render_template('management/post.html',title='岗位管理')

@management.route('/dept')
def dept():
    return render_template('management/dept.html',title='部门管理')

@management.route('/profile')
def profile():
    return render_template('management/profile.html',title='个人中心管理')