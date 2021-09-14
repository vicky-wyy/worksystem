from flask import Flask
from flask_login import LoginManager, login_manager
from flask_pymongo import PyMongo
from flask_mail import Mail
import smtplib
app = Flask(__name__)
# flask-login
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)

# MongoDB
mongo = PyMongo()
mongo.init_app(app,uri='mongodb://localhost:27017/stone')

# Flask-Mail
mail = Mail()
app.config['SECRET_KEY'] = 'shuguang'
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1954491067@qq.com'
app.config['MAIL_PASSWORD'] = 'hafyphmkseinbdgb'
app.config['SECURITY_EMAIL_SENDER'] = '1954491067@qq.com'
# mail注册到app中要放到配置后面
mail.init_app(app)

# 注册蓝图
from worksystem.modules.users import users
from worksystem.modules.management import management
app.register_blueprint(users)
app.register_blueprint(management)

from worksystem.modules.users import routes
from worksystem.modules.management import routes