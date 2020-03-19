#!/usr/bin/env python


from newnipt.server import *




@blueprint.route('/', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html')

@blueprint.route('/login/')
def login():
    callback_url = url_for('authorized', _external=True)
    return google.authorize(callback=callback_url)


@blueprint.route('/authorized')
@google.authorized_handler
def authorized(oauth_response):
    if oauth_response is None:
        flash("Access denied: reason={} error={}"
              .format(request.args['error_reason'],
                      request.args['error_description']))
        return abort(403)
    elif isinstance(oauth_response, OAuthException):
        #current_app.logger.warning(oauth_response.message)
        flash("{} - try again!".format(oauth_response.message))
        return redirect(url_for('index'))

    # add token to session, do it before validation to be able to fetch
    # additional data (like email) on the authenticated user
    session['google_token'] = (oauth_response['access_token'], '')

    # get additional user info with the access token
    google_user = google.get('userinfo') ## get google token
    google_data = google_user.data

    ## do stuff here

    return redirect(url_for('index'))
