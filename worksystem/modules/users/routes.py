from . import users
from worksystem.modules.management import management
from worksystem.modules.users.manage import verify_reset,verify_unexist,verify_exist,verify_login,verify_register
from flask import render_template,flash,redirect,url_for,request
from flask_login import current_user,login_user,logout_user
from worksystem.modules.users.definitions import LoginForm,RegisterRequestForm,RegisterForm,User,ResetPasswordRequestForm,ResetPasswordForm
from flask_login import login_required

# 登录
@users.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('您已经登录了')
        return redirect(url_for('management.index'))
    form = LoginForm()
    if form.validate_on_submit():
        itcode = request.form.get('itcode')
        print('用户名：：：：：：：：：：：：：')
        print(itcode)
        password = request.form.get('password')
        print('密码：：：：：：：：：：：：：：：：：：：')
        print(password)
        result = verify_login(itcode,password)
        print("结果：：：：：：：：：：：：：：")
        print(result)
        if result['code'] == 2:
            flash("该用户未注册，不能登录,请点击下方链接进行注册")
            return redirect(url_for('users.login'))
        if result['code'] == 0:
            flash("密码输入错误，请重新输入")
            return redirect(url_for('users.login'))
        if result['code'] == 3:
            flash('该用户账号已被禁用')
            return redirect(url_for('users.login'))
        user = User(result['result'])     
        login_user(user,remember=form.remember_me.data)
        return redirect(url_for('management.index'))
    return render_template('users/login.html',title='登录',form=form)

# 注册请求
@users.route('/register_request',methods=['GET', 'POST'])
def register_request():
    if current_user.is_authenticated:
        return redirect(url_for('management.index'))
    form = RegisterRequestForm()
    if form.validate_on_submit():
        itcode = request.form.get('itcode')
        result = verify_unexist(itcode)
        if result['code'] == 0:
            flash("该用户已注册,请直接登录")
            return redirect(url_for('users.login'))
        else:
            user = User({'itcode':itcode})
            # User.get_reset_password_token(user)
            User.register_email(user)
            flash("查看您的电子邮箱信息，以注册您的账号")
            return redirect(url_for('users.login'))
    return render_template('users/register_request.html',title='注册请求',form=form)

@users.route('/register',methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = verify_register(itcode=form.itcode.data,password=form.password.data)
        flash(result['msg'])
        return redirect(url_for('users.login'))
    return render_template('users/register.html',title='注册',form=form)

@users.route('/reset_password_request',methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        itcode = request.form.get('itcode')
        result = verify_exist(itcode)
        if result["code"] == 0:
            flash("该用户未注册，无法重置密码")
            return redirect(url_for("users.register"))
        else:
            user = User({"itcode":itcode})
            # User.get_reset_password_token(user)
            User.send_password_reset_email(user)
            flash(user.itcode+'查看您的电子邮箱信息，以重置您的密码')
            return redirect(url_for('users.login'))
    return render_template('users/reset_password_request.html',title='重置密码请求',form=form)

@users.route('/reset_password/<token>',methods=['GET' ,'POST'])
def reset_password(token):
    itcode = User.verify_reset_password_token(token)
    # 如果用户不存在，就进行注册
    if not itcode:
        flash("该用户不存在，请您先进行注册")
        return redirect(url_for('users.register'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        print('重置密码成功啦')
        password = request.form.get("password")
        result = verify_reset(itcode,password)
        flash('您的密码已经被重置，请用新密码登录您的账号')
        print("result==================================")
        print(result)
        return redirect(url_for('users.login'))
    return render_template('users/reset_password.html',title="重置密码",form=form)  

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))