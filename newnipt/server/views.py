#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app
from flask_login import login_user,logout_user, current_user, login_required
from .auto import app #login_manager, google, app, mail
from . import blueprint

app = current_app

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

    # match email against whitelist before completing sign up
    try:   
        user_obj =  User.query.filter_by(email = google_data['email']).first()
    except:
        user_obj = None
    if user_obj:
        try:
            if login_user(user_obj):
                return redirect(request.args.get('next') or url_for('batch'))
        except:
            flash('Sorry, you could not log in', 'warning')
    else:
        flash('Your email is not on the whitelist, contact an admin.')
        return redirect(url_for('index'))
    if login_user(user_obj):
        return redirect(request.args.get('next') or url_for('batch'))
    return redirect(url_for('index'))


@blueprint.route('/NIPT/')
@login_required
def batch():
    return render_template('start_page.html')