from app import app, db
from flask import Flask, redirect, url_for, session, g, render_template, flash, request
from flask_oauth import OAuth
from models import User
import json

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '555810068250-69s9rhvvu5uckg1vl4s2u7en4j7q73f2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'Qp6EokGG3FEuULXEoA07252f'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'development key'
oauth = OAuth()
app.secret_key = SECRET_KEY
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()
    


@app.route('/')
@app.route('/index')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v2/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
     
    resstr= res.read()
    resstr=resstr.rstrip('\n')
    
    d = json.loads(resstr)
    nome = d["name"]
    email = d["email"]
    uid = d["id"]
    print d.keys()
    
    user = User.query.filter_by(email=email).first()
        
    #print User.query.filter_by(email=email).first()
    
    if user is None: #L'utente non e' nel db
      print('Authentication failed.')
      session.pop('access_token', None)
      return redirect(url_for('login'))
    
    
    session['id'] =  user.id
    print session
    g.user = User.query.get(session['id'])
    #g.user = session['id']
    #g.user = User.query.get(1)
    #print g.user
    return render_template('index.html',user=user)
    #return res.read()
    
@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    print "dopo qui"
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    print "authorized"
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.before_request
def before_request():
    
    g.user = None
    if 'id' in session:
        print session['id']
        g.user = User.query.get(session['id'])
        print "uffa",g.user

@app.route('/logout')
def logout():
    session.pop('id', None)
    '''
    #https://accounts.google.com/o/oauth2/revoke?token={token}
    access_token = get_access_token()
    from urllib2 import Request, urlopen, URLError

    req = Request('https://accounts.google.com/o/oauth2/revoke?token='+access_token[0])
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            
            return redirect(url_for('login'))
        return res.read()
    '''    
    session.pop('access_token', None)
    #flash('You were signed out')
    return redirect(request.referrer or url_for('index'))
