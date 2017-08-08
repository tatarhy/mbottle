import os
from flask import Flask, session, render_template, url_for, g, flash, redirect
from flask_oauthlib.client import OAuth

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['MBOTTLE_SECRET_KEY']

oauth = OAuth()

zaim = oauth.remote_app(
    'zaim',
    consumer_key=os.environ['ZAIM_CONSUMER_KEY'],
    consumer_secret=os.environ['ZAIM_CONSUMER_SECRET'],
    request_token_url='https://api.zaim.net/v2/auth/request',
    access_token_url='https://api.zaim.net/v2/auth/access',
    authorize_url='https://auth.zaim.net/users/auth',
    base_url='https://api.zaim.net/v2/')

gmail = oauth.remote_app(
    'gmail',
    consumer_key=os.environ['GMAIL_CLIENT_ID'],
    consumer_secret=os.environ['GMAIL_CLIENT_SECRET'],
    request_token_url=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_method='POST',
    request_token_params={'scope': 'https://www.googleapis.com/auth/gmail.readonly'},
    base_url='https://www.googleapis.com/gmail/v1/')


@app.before_request
def before_request():
    g.user = None
    if 'zaim_token' in session:
        g.user = session['zaim_token']


@app.route("/")
def root():
    return render_template('connect.html')


@gmail.tokengetter
def get_gmail_token():
    return session['gmail_token']


@app.route("/connect/gmail")
def connect_gmail():
    callback_url = url_for('callback_gmail', _external=True)
    return gmail.authorize(callback=callback_url)


@app.route("/callback/gmail")
def callback_gmail():
    resp = gmail.authorized_response()
    if resp is None:
        return 'access denied'

    session['gmail_token'] = resp['access_token']
    return redirect(url_for('root'))


@zaim.tokengetter
def get_zaim_token():
    return session['zaim_token']


@app.route("/connect/zaim")
def connect_zaim():
    return zaim.authorize(callback=url_for('callback_zaim', _external=True))


@app.route("/callback/zaim")
def callback_zaim():
    resp = zaim.authorized_response()
    if resp is None:
        flash('error')
        return 'denied'

    session['zaim_token'] = (resp['oauth_token'], resp['oauth_token_secret'])

    return redirect(url_for('root'))


@app.route("/test")
def test():
    r = zaim.get('category')
    print(r)

    # return r.json()
    return ''


if __name__ == "__main__":
    app.run(debug=True)
