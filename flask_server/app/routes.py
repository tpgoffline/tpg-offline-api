from app import app
from flask import jsonify
from .models import *
    
@app.route('/')
def index():
    return "<h1>Welcome to tpg offline APNs Provider</h1>"

@app.route('/status/<device>')
def status(device):
	notifications = User.query.filter_by(device=device).all()
	response = []
	for notification in notifications:
		response.append({"line": notification.line, "fromHour": notification.fromHour, "toHour": notification.toHour, "days": notification.days})
	return jsonify(response)

@app.route('/add/<device>/<line>/<language>/<fromHour>/<toHour>/<days>')
def add(device, line, language, fromHour, toHour, days):
	if User.query.filter_by(device=device).filter_by(line=line).filter_by(fromHour=fromHour).filter_by(toHour=toHour).filter_by(days=days).first() == None:
		notification = User(device=device, line=line, language=language, fromHour=fromHour, toHour=toHour, days=days)
		db.session.add(notification)
		db.session.commit()
		return "1"
	else:
		return "0"

@app.route('/remove/<device>/<line>/<fromHour>/<toHour>/<days>')
def remove(device, line, fromHour, toHour, days):
	notification = User.query.filter_by(device=device).filter_by(line=line).filter_by(fromHour=fromHour).filter_by(toHour=toHour).filter_by(days=days).first()
	print(notification)
	if notification == None:
		return "0"
	else:
		db.session.delete(notification)
		db.session.commit()
		return "1"