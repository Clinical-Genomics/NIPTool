from werkzeug.contrib.fixers import ProxyFix

from newnipt.server import create_app

app = create_app()

app.wsgi_app = ProxyFix(app.wsgi_app)

from flask_mail import Mail
from flask_login import LoginManager


from flask_oauthlib.client import OAuth
#from .auto import app
#import ssl

#ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

mail = Mail(app)
login_manager = LoginManager(app)
oauth = OAuth(app)
google = oauth.remote_app('google', app_key='GOOGLE')
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.refresh_view = 'reauth' 