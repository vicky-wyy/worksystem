from bson.objectid import ObjectId
from worksystem import login_manager,mongo,mail
from worksystem import app
# Flask WTF
from flask import render_template,current_app
from threading import Thread
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired

# security
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
from time import time

# email
from flask_mail import Message

# Form表单
class LoginForm(FlaskForm):
    itcode = StringField('itcode地址',validators=[DataRequired()])
    password = PasswordField('密码',validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField("登录")

class RegisterRequestForm(FlaskForm):
    itcode = StringField('itcode',validators=[DataRequired()])
    submit = SubmitField('注册请求')

class RegisterForm(FlaskForm):
    itcode = StringField('ITcode',validators=[DataRequired()])
    password = PasswordField('密码',validators=[DataRequired()])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('注册')
    
class ResetPasswordRequestForm(FlaskForm):
    itcode = StringField('itcode',validators=[DataRequired()])
    submit = SubmitField('重置密码请求')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('密码',validators=[DataRequired()])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('重置密码')
    
class User(UserMixin):
    def __init__(self,user):
        self.itcode = user['itcode']
        # self.password_hash = user['password_hash']
        print('self.itcode is {}'.format(self.itcode))
        
    def get_id(self):
        return self.itcode 
    
    def __repr__(self):
        return (self.itcode) 
    
    @staticmethod
    def get(user_id):
        print('haha i am here')
        if not user_id:
            return None
        item = mongo.db.student.find_one(
            {
                "_id": ObjectId(user_id)
            }
        )
        if item is not None:
            return User(item)
        else:
            return None
    
    def get_itcode(itcode):
        if not itcode:
            return None
        item = mongo.db.student.find_one(
            {
                "itcode":itcode
            }
        )
        if item is not None:
            return User(item)
        else:
            return None
    # def check_password(self,password):
    #     return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self,expires_in=86400):
        return jwt.encode(
            {'reset_password':self.itcode,'exp':time()+expires_in},
            app.config['SECRET_KEY'],algorithm='HS256'
        )
    
        
    def verify_reset_password_token(token):
        try:
            itcode=jwt.decode(token,app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception as e:
            print(str(e))
            return 
        return User.get_itcode(itcode)
    
# email
    # def send_async_email(app,msg):
    #     with app.app_context(): 
    #             mail.send(msg)

    def send_email(subject,sender,recipients,text_body,html_body):
        msg = Message(subject,sender=sender,recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        # Thread(target=User.send_async_email,args=(app,msg)).start()
        mail.send(msg)
    
    def send_password_reset_email(user):
        token = user.get_reset_password_token()
        User.send_email('[用户管理系统] 重置密码',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[user.itcode+('@sugon.com')],
                text_body=render_template('email/reset_password.txt',
                                         user=user,token=token),
                html_body=render_template('email/reset_password.html',
                                         user=user,token=token))
        
    def register_email(user):
        token = user.get_reset_password_token()
        User.send_email('[用户管理系统] 注册',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[user.itcode+('@sugon.com')],
                text_body=render_template('email/register_itcode.txt',
                                         user=user,token=token),
                html_body=render_template('email/register_itcode.html',
                                         user=user,token=token))

@login_manager.user_loader
def load_user(itcode):
    print('load user, trying to get User from itcode: {}'.format(itcode))
    user = User.get_itcode(itcode)
    return user
