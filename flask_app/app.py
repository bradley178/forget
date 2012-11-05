from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException
from flask import Flask, redirect, render_template, request, session, url_for
from forget.evernote_client import EvernoteClient
from forget.todo.list import List
import oauth2 as oauth
import os
import urllib
import urlparse

app = Flask(__name__)

APP_SECRET_KEY = os.environ.get('FORGET_APP_SECRET')
EVERNOTE_CONSUMER_KEY = os.environ.get('FORGET_EVERNOTE_CONSUMER_KEY')
EVERNOTE_CONSUMER_SECRET = os.environ.get('FORGET_EVERNOTE_CONSUMER_SECRET')

EVERNOTE_URL = 'https://sandbox.evernote.com'

def get_oauth_client(token=None):    
    consumer = oauth.Consumer(EVERNOTE_CONSUMER_KEY, EVERNOTE_CONSUMER_SECRET)
    if token:
        client = oauth.Client(consumer, token)
    else:
        client = oauth.Client(consumer)
    return client


def require_evernote_auth(fn):
    def handle_auth_error():
        try:
            return fn()
        except EDAMUserException, e:
            if e.errorCode == EDAMErrorCode.DATA_REQUIRED: 
                return redirect("/auth")
            else:
                raise
    return handle_auth_error

@app.route('/auth')
def auth_start():
    client = get_oauth_client()

    # Make the request for the temporary credentials (Request Token)
    callback_url = 'http://%s%s' % ('127.0.0.1:5000', url_for('auth_finish'))
    request_url = '%s?oauth_callback=%s' % (EVERNOTE_URL + '/oauth',
        urllib.quote(callback_url))

    resp, content = client.request(request_url, 'GET')

    if resp['status'] != '200':
        raise Exception('Invalid response %s.' % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    # Save the request token information for later
    session['oauth_token'] = request_token['oauth_token']
    session['oauth_token_secret'] = request_token['oauth_token_secret']

    # Redirect the user to the Evernote authorization URL
    return redirect('%s?oauth_token=%s' % (EVERNOTE_URL + '/OAuth.action',
        urllib.quote(session['oauth_token'])))


@app.route('/authComplete')
def auth_finish():
    oauth_verifier = request.args.get('oauth_verifier', '')

    token = oauth.Token(session['oauth_token'], session['oauth_token_secret'])
    token.set_verifier(oauth_verifier)

    client = get_oauth_client()
    client = get_oauth_client(token)

    # Retrieve the token credentials (Access Token) from Evernote
    resp, content = client.request(EVERNOTE_URL + '/oauth', 'POST')

    if resp['status'] != '200':
        raise Exception('Invalid response %s.' % resp['status'])

    access_token = dict(urlparse.parse_qsl(content))
    authToken = access_token['oauth_token']

    session['evernote_token'] = authToken

    return redirect("/")

@app.route("/")
@require_evernote_auth
def index():
    client = EvernoteClient(EVERNOTE_URL, session.get('evernote_token'))
    list = List(client.note_store, client.authtoken)

    return render_template('index.html', tasks=list.tasks_by_expiration())

if __name__ == "__main__":
    app.secret_key = APP_SECRET_KEY
    app.run(debug=True)

