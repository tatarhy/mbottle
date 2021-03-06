import base64
import os
from flask import Flask, session, render_template, url_for, g, flash, redirect, jsonify
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


@app.route("/disconnect/gmail")
def disconnect_gmail():
    session.pop('gmail_token')
    return redirect(url_for('root'))


@app.route("/callback/gmail")
def callback_gmail():
    resp = gmail.authorized_response()
    if resp is None:
        return 'access denied'

    session['gmail_token'] = (resp['access_token'], '')
    return redirect(url_for('root'))


@zaim.tokengetter
def get_zaim_token():
    return session['zaim_token']


@app.route("/connect/zaim")
def connect_zaim():
    return zaim.authorize(callback=url_for('callback_zaim', _external=True))


@app.route("/disconnect/zaim")
def disconnect_zaim():
    session.pop('zaim_token')
    return redirect(url_for('root'))


@app.route("/callback/zaim")
def callback_zaim():
    resp = zaim.authorized_response()
    if resp is None:
        flash('error')
        return 'denied'

    session['zaim_token'] = (resp['oauth_token'], resp['oauth_token_secret'])

    return redirect(url_for('root'))


@app.route("/messages")
def messages():
    messages = gmail.get('users/me/messages')
    return render_template('messages.html', messages=messages.data)


@app.route("/messages/<id>")
def message_body(id):
    mes = gmail.get('users/me/messages/'+id)
    z = mes.data['payload']
    if z['mimeType'] == 'multipart/alternative':
        p = ''.join([i['body']['data'].rstrip() for i in z['parts'] if i['mimeType'] == 'text/html'])
        pp = base64.urlsafe_b64decode(p)
    return pp


@app.route("/messages/<id>.json")
def message_json(id):
    mes = gmail.get('users/me/messages/'+id)
    z = mes.data
    return jsonify(z)


if __name__ == "__main__":
    app.run(debug=True)
