from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

orarioIngresso = "10:30"
maxOrarioIngr = "14:00"
maxNumOre = 11
minNumOre = 7

FMT = '%H:%M'

from app import views, models
import datetime
#from datetime import datetime, date

def orePresenza(entrata, uscita, data):
  return datetime.datetime.combine(data, uscita) - datetime.datetime.combine(data, entrata)

def ritardo(entrata, data):
  if datetime.datetime.strptime(entrata.strftime("%H:%M"), FMT) <= datetime.datetime.strptime(orarioIngresso, FMT):
    return "0:00:00"
  else: 
    return datetime.datetime.strptime(entrata.strftime("%H:%M"), FMT) - datetime.datetime.strptime(orarioIngresso, FMT)

def oreGiornaliereValide(entrata, uscita):
  entrata = datetime.datetime.strptime(entrata.strftime("%H:%M"), FMT)
  uscita = datetime.datetime.strptime(uscita.strftime("%H:%M"), FMT)
  ingressoOk = datetime.datetime.strptime(orarioIngresso, FMT)
  maxOre = datetime.timedelta(hours=maxNumOre)
  minOre = datetime.timedelta(hours=minNumOre)
  oreTot=uscita-entrata
  if (entrata<=ingressoOk):    
    return oreTot<=maxOre and oreTot or maxOre
  else:
    return oreTot<=minOre and oreTot or minOre

def ROL(entrata):
  entrata = datetime.datetime.strptime(entrata.strftime("%H:%M"), FMT)
  ingressoMax = datetime.datetime.strptime(maxOrarioIngr, FMT)
  ingressoOk = datetime.datetime.strptime(orarioIngresso, FMT)
  if(entrata>=ingressoMax):
    return entrata-ingressoOk
  else:
    return 0
  

app.jinja_env.globals.update(orePresenza=orePresenza)
app.jinja_env.globals.update(ritardo=ritardo)
app.jinja_env.globals.update(oreGiornaliereValide=oreGiornaliereValide)
app.jinja_env.globals.update(ROL=ROL)
