from app import db
from app.constants import * 
import constants as constants
import datetime
from sqlalchemy import extract


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    entrate = db.relationship('Entrata', backref='user', lazy='dynamic')
    uscite = db.relationship('Uscita', backref='user', lazy='dynamic')
    
    def entra(self,entrata):
      #Controllare se c'e' gia' un'entrata nella giornata, in tal caso rifiutare l'ingresso
      #self.entrate.filter(self.entrate.c.data==entrata.data)
      for entry in self.entrate:
        if entry.data==entrata.data:
          print "OK"
        else:
          print "non Ok"
      self.entrate.append(entrata)
      return self
      
    def esci(self,uscita):
      #Controllare se c'e' gia' un'uscita nella giornata, in tal caso sostituire l'uscita
      self.uscite.append(uscita)
      return self
    
    #def entrate_uscite_totali(self):
      #(db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
      #return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id)).all()
      
    def entrate_uscite_totali(self, mese=None):
      #(db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
      if mese==None:
        return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id)).all()
      return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id).filter(extract('month',Entrata.data)== mese)).all()
      
    def orePresenzaGiornaliere(self,data):
      entrata = datetime.datetime.strptime(Entrata.query.filter(Entrata.data == data).filter(Entrata.user_id == self.id).first().ora.strftime("%H:%M"), FMT) 
      uscita = datetime.datetime.strptime(Uscita.query.filter(Uscita.data == data).filter(Uscita.user_id == self.id).first().ora.strftime("%H:%M"), FMT) 
      return uscita - entrata 
    
    def oreGiornaliereValide(self,data):
      #TODO controllo se data non e' presente in db
      uscita = datetime.datetime.strptime(Uscita.query.filter(Uscita.data == data).filter(Uscita.user_id == self.id).first().ora.strftime("%H:%M"), FMT) 
      entrata = datetime.datetime.strptime(Entrata.query.filter(Entrata.data == data).filter(Entrata.user_id == self.id).first().ora.strftime("%H:%M"), FMT)
      ingressoOk = datetime.datetime.strptime(orarioIngresso, FMT)
      maxOre = datetime.timedelta(hours=maxNumOre)
      minOre = datetime.timedelta(hours=minNumOre)
      oreTot=uscita-entrata
      if (entrata<=ingressoOk):    
        return oreTot<=maxOre and oreTot or maxOre
      else:
        return oreTot<=minOre and oreTot or minOre
      
    def oreMensiliDaRecuperare(self, mese):
      entries = self.entrate_uscite_totali(mese)
      oreTotali = datetime.timedelta(hours=0)
      oreDovute = datetime.timedelta(hours=len(entries)*minNumOre)
      for entry in entries:
        oreTotali+=self.oreGiornaliereValide(entry.Entrata.data)
      if oreTotali>oreDovute: 
        return None
        
      return oreDovute-oreTotali
      
      '''
      entrata = datetime.datetime.strptime(entrata, FMT)
      uscita = datetime.datetime.strptime(uscita, FMT)
      ingressoOk = datetime.datetime.strptime(orarioIngresso, FMT)
      maxOre = datetime.timedelta(hours=maxNumOre)
      minOre = datetime.timedelta(hours=minNumOre)
      oreTot=uscita-entrata
      if (entrata<=ingressoOk):    
        return oreTot<=maxOre and oreTot or maxOre
      else:
        return oreTot<=minOre and oreTot or minOre
      '''
      return 0
    
    def __repr__(self):
        return '<User %r>' % (self.nome)
'''        
class Orario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ora = db.Column(db.String(64), index=True, unique=True)
    data = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<User %r>' % (self.nome)
'''        
class Entrata(db.Model):
    __tablename__ = 'entrata'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data = db.Column(db.Date)
    ora = db.Column(db.Time)
    
    def ritardo(self):
      if datetime.datetime.strptime(self.ora.strftime("%H:%M"), FMT) <= datetime.datetime.strptime(orarioIngresso, FMT):
        return "0:00:00"
      else: 
        return datetime.datetime.strptime(self.ora.strftime("%H:%M"), FMT) - datetime.datetime.strptime(orarioIngresso, FMT)
    
    def ROL(self):
      orarioIngresso = datetime.datetime.strptime(constants.orarioIngresso, FMT)
      entrata = datetime.datetime.strptime(self.ora.strftime(FMT), FMT)
      
      maxRitardo = datetime.datetime.strptime(maxOrarioIngr, FMT) - orarioIngresso
      ritardo = self.ritardo()
      if ritardo >= maxRitardo:
        return entrata - orarioIngresso
      else:
        return datetime.timedelta(0)
      
    
    def __repr__(self):
        return (self.ora.strftime("%H:%M"))
        
class Uscita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data = db.Column(db.Date)
    ora = db.Column(db.Time)
    
    def orePresenza(self,entrata):
      return datetime.datetime.strptime(self.ora.strftime("%H:%M"), FMT) - datetime.datetime.strptime(entrata, FMT)
    
    def __repr__(self):
        return (self.ora.strftime("%H:%M"))

'''        
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
'''
