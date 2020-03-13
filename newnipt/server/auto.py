from werkzeug.contrib.fixers import ProxyFix

from newnipt.server import create_app

app = create_app()

app.wsgi_app = ProxyFix(app.wsgi_app)


