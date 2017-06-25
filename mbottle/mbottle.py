import os
from flask import Flask, request, session, render_template
from rauth import OAuth1Service

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['MBOTTLE_SECRET_KEY']

zaim = OAuth1Service(
    name='zaimtestt1',
    consumer_key=os.environ['ZAIM_CONSUMER_KEY'],
    consumer_secret=os.environ['ZAIM_CONSUMER_SECRET'],
    request_token_url='https://api.zaim.net/v2/auth/request',
    access_token_url='https://api.zaim.net/v2/auth/access',
    authorize_url='https://auth.zaim.net/users/auth',
    base_url='https://api.zaim.net/v2')


@app.route("/")
def root():
    request_token, request_token_secret = zaim.get_request_token(
        params={'oauth_callback': 'http://localhost:5000/callback/zaim'})
    session['request_token'] = request_token
    session['request_token_secret'] = request_token_secret
    zaim_auth_url = zaim.get_authorize_url(request_token)
    return render_template('connect.html', zaim_auth_url=zaim_auth_url)


@app.route("/callback/zaim")
def callback_zaim():
    oauth_token = request.args['oauth_token']
    oauth_verifier = request.args['oauth_verifier']

    request_token = session['request_token']
    request_token_secret = session['request_token_secret']

    auth_session = zaim.get_auth_session(request_token, request_token_secret, params={'oauth_verifier': oauth_verifier})
    session['access_token'] = auth_session.access_token
    session['access_token_secret'] = auth_session.access_token_secret

    return ''


@app.route("/test")
def test():
    auth_session = zaim.get_session((session['access_token'], session['access_token_secret']))

    r = auth_session.get('https://api.zaim.net/v2/category', params={'format': 'json'})
    print(r.json())

    # return r.json()
    return ''


if __name__ == "__main__":
    app.run(debug=True)
