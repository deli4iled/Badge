from app import app
from flask import Flask, redirect, url_for, session, render_template, request, g, flash, abort
from flask_oauth import OAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '555810068250-69s9rhvvu5uckg1vl4s2u7en4j7q73f2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'Qp6EokGG3FEuULXEoA07252f'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.config.update(
    DATABASE_URI = 'sqlite:///users.db',
    #SECRET_KEY = 'development key',
    #DEBUG = True
)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

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

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid

'''
@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    pass
'''

@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    print res.read()
    #g.user = res.read()['name']
    #TODO: qui bisogna controllare se l'email e' presente nel db
    return render_template('index.html')


@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)



@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
