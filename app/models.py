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
      
    def entrate_uscite_totali(self, mese=None, anno=None):
      #(db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== g.user.id)).all()
      if mese==None and anno==None:
        return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id)).all()
      if mese==None:
        return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id).filter(extract('year',Entrata.data)== anno)).all()
      if anno==None:
        return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id).filter(extract('month',Entrata.data)== mese)).all()
      return (db.session.query(User, Entrata, Uscita).join(Entrata).join(Uscita, Entrata.data == Uscita.data).filter(Entrata.user_id==Uscita.user_id).filter(User.id== self.id).filter(extract('month',Entrata.data)== mese).filter(extract('year',Entrata.data)== anno)).all()
      
    def orePresenzaGiornaliere(self,data):
      entrata = datetime.datetime.strptime(Entrata.query.filter(Entrata.data == data).filter(Entrata.user_id == self.id).first().ora.strftime("%H:%M"), FMT) 
      uscita = datetime.datetime.strptime(Uscita.query.filter(Uscita.data == data).filter(Uscita.user_id == self.id).first().ora.strftime("%H:%M"), FMT) 
      return uscita - entrata 
    
    def oreMensiliTotali(self, mese, anno, entries=None):
      if entries==None:
        entries = self.entrate_uscite_totali(mese, anno)
      oreTotali = datetime.timedelta(hours=0)
      for entry in entries:
        oreTotali+=self.orePresenzaGiornaliere(entry.Entrata.data)      
      return oreTotali
    
    def oreGiornaliereValide(self,data):
      #TODO controllo se data non e' presente in db
      uscita = datetime.datetime.strptime(Uscita.query.filter(Uscita.data == data).filter(Uscita.user_id == self.id).first().ora.strftime("%H:%M"), FMT) 
      entrata = datetime.datetime.strptime(Entrata.query.filter(Entrata.data == data).filter(Entrata.user_id == self.id).first().ora.strftime("%H:%M"), FMT)
      ingressoOk = datetime.datetime.strptime(orarioIngresso, FMT)
      maxOre = datetime.timedelta(hours=maxNumOre)
      minOre = datetime.timedelta(hours=minNumOre)
      oreTot=uscita-entrata
      if oreTot == datetime.timedelta(0):
        return oreTot
      if (entrata<=ingressoOk):    
        return oreTot<=maxOre and oreTot or maxOre
      else:
        return oreTot<=minOre and oreTot or minOre
      
    def oreDovuteMese(self, mese, anno, entries=None):
      if entries==None:
        entries = self.entrate_uscite_totali(mese, anno)
      return datetime.timedelta(hours=len(entries)*minNumOre)      
    
    def oreMensiliDaRecuperare(self, mese,anno):
     
      totale= self.oreDovuteMese(mese,anno)-self.oreMensiliValide(mese,anno)+self.totaleRitardi(mese,anno)
      print totale
      if totale < datetime.timedelta(0):
        return None
      return totale
       
    
    def oreMensiliValide(self, mese, anno, entries=None):
      if entries==None:
        entries = self.entrate_uscite_totali(mese, anno)
      oreTotali = datetime.timedelta(hours=0)
      for entry in entries:
        oreTotali+=self.oreGiornaliereValide(entry.Entrata.data)
      
      return oreTotali
    
    
    def totaleRitardi(self, mese, anno, entries=None):
      if entries==None:
        entries = self.entrate_uscite_totali(mese, anno)
      ritardiTotali = datetime.timedelta(hours=0)
      for entry in entries:
        ritardiTotali+=entry.Entrata.ritardoNoROL()
      return ritardiTotali
      
    def ROLMensili(self, mese, anno,entries):
      if entries==None:
        entries = self.entrate_uscite_totali(mese, anno)
      ROLTotali = datetime.timedelta(hours=0)
      for entry in entries:
        ROLTotali+=entry.Entrata.ROL()
      return ROLTotali
      
    def avg(self, mese, anno,entries):
      if entries==None:
        entries = self.entrate_uscite_totali(mese, anno)
      sumEntrate = 0
      sumUscite = 0
      for entry in entries:
        sumEntrate+=entry.Entrata.ora.hour*3600+entry.Entrata.ora.minute*60 
        sumUscite+=entry.Uscita.ora.hour*3600+entry.Uscita.ora.minute*60
     
      avgEntrate=sumEntrate/len(entries)
      avgUscite=sumUscite/len(entries)
      return {'entrata':datetime.timedelta(seconds=avgEntrate), 'uscita':datetime.timedelta(seconds=avgUscite)}
      #return sumEntrate/len(entry),sumUscite/len(entry) 
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
      #se e' ROL non e' ritardo
      if datetime.datetime.strptime(self.ora.strftime("%H:%M"), FMT) <= datetime.datetime.strptime(orarioIngresso, FMT):
        return datetime.timedelta(0)
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
        
    def ritardoNoROL(self):
      orarioIngresso = datetime.datetime.strptime(constants.orarioIngresso, FMT)
      entrata = datetime.datetime.strptime(self.ora.strftime(FMT), FMT)
      
      maxRitardo = datetime.datetime.strptime(maxOrarioIngr, FMT) - orarioIngresso
      ritardo = self.ritardo()
      
      if ritardo >= maxRitardo:
        return datetime.timedelta(0)
      else:
        return ritardo
      
    
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
