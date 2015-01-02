from app import app, db
from flask import Flask, redirect, url_for, session, g, render_template, flash, request
from flask_oauth import OAuth
from models import User, Entrata, Uscita
import json

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '555810068250-69s9rhvvu5uckg1vl4s2u7en4j7q73f2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'Qp6EokGG3FEuULXEoA07252f'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console
feste = [6,95,96,115,121,153,180,227,305,342,359,360]

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
    
    return render_template('index.html')
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
    flash('Logout eseguito con successo')
    return redirect(url_for('index'))
    
@app.route('/overview')
def overview():
  #cur = db.execute('select title, text from entries order by id desc')
  #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
  #entries = (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(User.id== g.user.id)).all()
  #entries = (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data, Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
  entries = (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
  
  print "qui",entries
  return render_template('show_entries.html', entries=entries)
  
@app.route('/checkin/entra', methods=["GET", "POST"])
def entra():
  import datetime
  
  oggi = datetime.datetime.now()
  
  f = request.form
  if f:
    print f['entrata']
    oggi = datetime.datetime.strptime(f['data']+" "+f['entrata'],"%d/%m/%y %H:%M")
  #for key in f.keys():
  #  for value in f.getlist(key):
  #      print key,":",value
  else:
    ieri = oggi.date()-datetime.timedelta(1)
    trovato=False
    for entry in g.user.uscite:
      if entry.data==ieri:
        trovato=True
        flash(entry.data)
        flash(entry.ora)
        
        break
    if not trovato:
      flash("Il checkin in uscita ieri non e' stato effettuato")
      entries = (db.session.query(User, Entrata).join(Entrata,Entrata.data == ieri).filter(Entrata.user_id==User.id).filter(User.id== g.user.id)).all()
      flash(entries)
      return render_template('add_entry.html', entries=entries, entrata=True)
  
  giorno = oggi.timetuple()
  
  if (giorno.tm_wday==5 or giorno.tm_wday==6 or giorno.tm_yday in feste):
    flash("Giorno non lavorativo")
    return render_template('checkin.html')
  entrata = Entrata(user_id=g.user.id, data=oggi.date(),ora=oggi.time())
  for entry in g.user.entrate:
    if entry.data==entrata.data:
     flash("Il checkin in ingresso oggi e' gia' stato effettuato")
     return render_template('checkin.html')
  
  g.user.entra(entrata)
  db.session.commit()
  flash(entrata)
  return render_template('checkin.html')
@app.route('/checkin/esci', methods=["GET", "POST"])
def esci():
  import datetime
  
  oggi = datetime.datetime.now()
  
  f = request.form
  if f:
    print f['uscita']
    oggi = datetime.datetime.strptime(f['data']+" "+f['uscita'],"%d/%m/%y %H:%M")
  #for key in f.keys():
  #  for value in f.getlist(key):
  #      print key,":",value
  else:
    
    trovato=False
    for entry in g.user.entrate:
      if entry.data==oggi.date():
        trovato=True
    if not trovato:
      flash("Il checkin in entrata oggi non e' stato effettuato")
      #entries = (db.session.query(User, Entrata).join(Entrata,Entrata.data == oggi).filter(Entrata.user_id==User.id).filter(User.id== g.user.id)).all()
      entries = []
      res = Entrata(user_id=g.user.id, data=oggi.date(),ora=oggi.time())
      flash(entries)
      return render_template('add_entry.html', entries=entries, res=res)
  
  giorno = oggi.timetuple()
  
  if (giorno.tm_wday==5 or giorno.tm_wday==6 or giorno.tm_yday in feste):
    flash("Giorno non lavorativo")
    return render_template('checkin.html')


  uscita = Uscita(user_id=g.user.id, data=oggi.date(),ora=oggi.time())
  for entry in g.user.uscite:
    if entry.data==uscita.data:
     flash("Il checkin in uscita  di oggi e' stato posticipato")
     db.session.delete(entry)
     break
  
  g.user.esci(uscita)
  db.session.commit()
  flash(uscita)
  return render_template('checkin.html')
@app.route('/checkin')
def checkin():
  return render_template('checkin.html')
