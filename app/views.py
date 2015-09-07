from app import app, db
from flask import Flask, redirect, url_for, session, g, render_template, flash, request
from functools import wraps
from sqlalchemy import extract
from flask_oauth import OAuth
from models import User, Entrata, Uscita
import datetime  

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()
    


@app.route('/')
@app.route('/index')
def index():
    #flash(session)
    if g.user:
      
      entrata = None
      uscita = None
      entries = entriesMese()
      
      if session.get('data'): 
        if session['data']!= str(datetime.datetime.now().date()): #le entry sono antecedenti ad oggi
          session.pop('data')
          session.pop('entrata')
          session.pop('uscita')              
        else:
          if session.get('entrata'):
            entrato = True
            entrata = session['entrata']
            if session.get('uscita'):
              uscita = True
              uscita = session['uscita']
        #flash(uscita,entrata)
      else:
        entrato, entrata = checkEntrata()
        uscito, new_uscita, uscita = checkUscita()
        #flash(uscito)
        if entrato:
          session['entrata'] = str(entrata)
          session['data'] = str(datetime.datetime.now().date())
          if uscito: 
            session['uscita'] = str(uscita)
          else:
            uscita = None
        else:
          entrata = None
      return render_template('index.html',entrata=str(entrata), uscita=str(uscita), entries=entries)
    return render_template('index.html')
    
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
      flash("Accesso negato - utente non autorizzato")
      return redirect(url_for('index'))
    
    
    session['id'] =  user.id
    print session
    g.user = User.query.get(session['id'])
    #g.user = session['id']
    #g.user = User.query.get(1)
    #print g.user
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
    session.pop('id', None) #forse togliere
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
    session.pop('access_token', None) #forse togliere
    session.clear()
    flash('Logout eseguito con successo')
    return redirect(url_for('index'))
    
@app.route('/overview')
@app.route('/overview/<month>/<year>')
@login_required
def overview(month=datetime.datetime.now().date().month,year=datetime.datetime.now().date().year):
  
  #entries = (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
  #entries = g.user.entrate_uscite_totali()
  #print "qui",entries
  return render_template('show_entries.html', sel_month=month, sel_year=year)
  
@app.route('/global_overview')
@app.route('/global_overview/<month>/<year>')
@login_required
def global_overview(month=datetime.datetime.now().date().month,year=datetime.datetime.now().date().year):
  
  #entries = (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
  #entries = g.user.entrate_uscite_totali()
  #print "qui",entries
  return render_template('show_entries_global.html', sel_month=month, sel_year=year)
  
@app.route('/entra')
@login_required
def entra():
  entrato, entrata = checkEntrata()
  if not entrato:
    g.user.entra(entrata)
    db.session.commit()
    session['entrata'] = str(entrata)
    session['data'] = str(datetime.datetime.now().date())
    #flash(str(session))
  return redirect(url_for('index'))
  
@app.route('/esci')
@login_required
def esci():  
  if  session.get('entrata'):    
    uscito, uscita, entry = checkUscita()
    #flash('Registrazione entrata avvenuta')
    if uscito:
       flash("Il checkin in uscita  di oggi e' stato posticipato")
       db.session.delete(entry)
    g.user.esci(uscita)
    db.session.commit()
    session['uscita'] = str(uscita)
    session['data'] = str(datetime.datetime.now().date())
    #flash(str(uscita))
  return redirect(url_for('index'))

@app.route('/statistiche')
@login_required
def statistiche():
  return render_template('statistiche.html')

@app.context_processor
def up_date():
    def date_now():
        return datetime.datetime.now().date()
    return dict(date_now=date_now)

@app.context_processor
def up_years():
    def years():
      starting_year = datetime.datetime(2010,1,1).year
      current_year = datetime.datetime.now().date().year
      delta = current_year - starting_year
      years = []
      for i in range(delta+1):
        years.append(starting_year+i)
      print years
      return years
    return dict(years=years)
    
@app.context_processor
def up_months():
    def months():
      months = [ "Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]
      curr_month = datetime.datetime.now().date().month
      '''
        starting_year = datetime.datetime(2010,1,1).year
        current_year = datetime.datetime.now().date().year
        delta = current_year - starting_year
        years = []
        for i in range(delta+1):
          years.append(starting_year+i)
      '''
      print curr_month
      return months
    return dict(months=months)
#@app.route('/checkin')
#def checkin():
#  entrato, entrata = checkEntrata()
#  flash(str(checkEntrata())+" "+str(checkUscita()))
#  return render_template('index.html', entrato=entrato, uscito=checkUscita())


#Utilities: spostare
def checkEntrata():
  entrata = Entrata(user_id=g.user.id, data=datetime.datetime.now().date(),ora=datetime.datetime.now().time())
  for entry in g.user.entrate:
    if entry.data==entrata.data:
     return True, entry
  return False, entrata
  
def checkUscita():
  uscita = Uscita(user_id=g.user.id, data=datetime.datetime.now().date(),ora=datetime.datetime.now().time())
  for entry in g.user.uscite:
    if entry.data==uscita.data:
     #flash("Gia' uscito")
     return True, uscita, entry
  return False, uscita, None

def entriesMese():
  data=datetime.datetime.now().date().month
  return (db.session.query(Entrata, Uscita).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id).filter(extract('month', Entrata.data)==data)).all()


