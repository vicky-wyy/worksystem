from flask import Blueprint

management = Blueprint('management',__name__,url_prefix='/management')

from . import routes