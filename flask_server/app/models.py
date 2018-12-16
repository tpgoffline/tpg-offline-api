from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(64), index=True)
    line = db.Column(db.String(64), index=True)
    fromHour = db.Column(db.String(64), index=True)
    toHour = db.Column(db.String(64), index=True)
    days = db.Column(db.String(64), index=True)
    language = db.Column(db.String(5), index=True)
    sandbox = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<User {}>'.format(self.device)

class Reminder(db.Model):
    __tablename__ = 'reminders'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(64), index=True)
    departureCode = db.Column(db.Integer, index=True)
    sentHour = db.Column(db.String(5), default=None)
    sentDate = db.Column(db.String(11), default=None)
    sent = db.Column(db.Boolean(), default=False, index=True)
    title = db.Column(db.String(100))
    estimatedArrivalTime = db.Column(db.String(5))
    text = db.Column(db.String(1000))
    line = db.Column(db.String(8))
    reminderTimeBeforeDeparture = db.Column(db.Integer)
    stopCode = db.Column(db.String(5))
    sandbox = db.Column(db.Boolean(), default=False)
    x = db.Column(db.Float, default=None)
    y = db.Column(db.Float, default=None)
    stopName = db.Column(db.String(1000))

    def __repr__(self):
        return '<Reminder {}>'.format(self.device)

class Notification(db.Model):
    __tablename__ = 'notifications_sent'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(64), index=True)
    line = db.Column(db.String(8))
    date = db.Column(db.String(11))
    hour = db.Column(db.String(11))
    title = db.Column(db.String(500))
    text = db.Column(db.String(500))

    def __repr__(self):
        return '<Notification {}>'.format(self.device)
