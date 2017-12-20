from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(64), index=True)
    line = db.Column(db.String(64), index=True)
    fromHour = db.Column(db.String(64), index=True)
    toHour = db.Column(db.String(64), index=True)
    days = db.Column(db.String(64), index=True)
    language = db.Column(db.String(5), index=True)

    def __repr__(self):
        return '<User {}>'.format(self.device)