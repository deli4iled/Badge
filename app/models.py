from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    entrate = db.relationship('Entrata', backref='utente', lazy='dynamic')
    uscite = db.relationship('Uscita', backref='utente', lazy='dynamic')
    
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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data = db.Column(db.Date)
    ora = db.Column(db.Time)
    
    def __repr__(self):
        return '<Entrata %r>' % (self.ora)
        
class Uscita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data = db.Column(db.Date)
    ora = db.Column(db.Time)
    
    def __repr__(self):
        return '<Uscita %r>' % (self.ora)

'''        
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
'''
