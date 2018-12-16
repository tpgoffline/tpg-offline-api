from app import app
from flask import jsonify, redirect
from flask import request, abort, render_template
from .models import *
import requests
import json
from difflib import SequenceMatcher
from datetime import datetime
from threading import Thread
import dateutil.parser
import requests

stops = requests.get("https://raw.githubusercontent.com/tpgoffline/tpgoffline-data/master/stops.json").json()
departures = requests.get("https://raw.githubusercontent.com/tpgoffline/tpgoffline-data/master/departures.json").json()
    
@app.route('/')
def index():
    return render_template("index.html")

# Disruptions Monitoring

@app.route('/disruptionsmonitoring/<device>', methods=['GET'])
def status(device):
	notifications = User.query.filter_by(device=device).all()
	response = []
	for notification in notifications:
		response.append({"line": notification.line, "fromHour": notification.fromHour, "toHour": notification.toHour, "days": notification.days})
	return jsonify(response)

@app.route('/disruptionsmonitoring/<device>', methods=['POST'])
def add(device):
	try:
		lines = request.form["lines"].split(":")
		language = request.form["language"]
		fromHour = request.form["fromHour"]
		toHour = request.form["toHour"]
		days = request.form["days"]
		sandbox = False
		for line in lines:
			if User.query.filter_by(device=device).filter_by(line=line).filter_by(fromHour=fromHour).filter_by(toHour=toHour).filter_by(days=days).first() == None:
				notification = User(device=device, line=line, language=language, fromHour=fromHour, toHour=toHour, days=days, sandbox=sandbox)
				db.session.add(notification)
				db.session.commit()
			else:
				return "0"
		return "1"
	except Exception as e:
		return "-1"

@app.route('/disruptionsmonitoring/<device>', methods=['DELETE'])
def remove(device):
	try:
		line = request.values["line"]
		fromHour = request.values["fromHour"]
		toHour = request.values["toHour"]
		days = request.values["days"]
		sandbox = False
		notification = User.query.filter_by(device=device).filter_by(line=line).filter_by(fromHour=fromHour).filter_by(toHour=toHour).filter_by(days=days).first()
		if notification == None:
			return "0"
		else:
			db.session.delete(notification)
			db.session.commit()
			return "1"
	except Exception as e:
		return "-1"

# Reminders

@app.route('/reminders/<device>', methods=['GET'])
def remindersStatus(device):
	reminders = Reminder.query.filter_by(device=device).filter_by(sent=False).all()
	response = []
	for reminder in reminders:
		response.append({"estimatedTriggerTime": datetime.strptime(reminder.estimatedArrivalTime, "%H:%M").replace(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day).strftime("%H:%M"), "title": reminder.title, "text": reminder.text, "id": reminder.id})
	return jsonify(response)

@app.route('/reminders/<device>', methods=['POST'])
def remindersAdd(device):
	try:
		departureCode = request.form["departureCode"]
		title = request.form["title"]
		text = request.form["text"]
		line = request.form["line"]
		reminderTimeBeforeDeparture = request.form["reminderTimeBeforeDeparture"]
		stopCode = request.form["stopCode"]
		sandbox = False
		estimatedArrivalTime = request.form["estimatedArrivalTime"]
		if Reminder.query.filter_by(device=device).filter_by(departureCode=departureCode).filter_by(title=title).filter_by(text=text).filter_by(line=line).filter_by(reminderTimeBeforeDeparture=reminderTimeBeforeDeparture).filter_by(stopCode=stopCode).first() == None:
			reminder = Reminder(device=device, departureCode=departureCode, title=title, text=text, line=line, reminderTimeBeforeDeparture=reminderTimeBeforeDeparture, stopCode=stopCode, estimatedArrivalTime=estimatedArrivalTime, sandbox=sandbox)
			db.session.add(reminder)
			db.session.commit()
			return "1"
		else:
			return "0"
	except Exception as e:
		return "-1"

@app.route('/reminders/<device>', methods=['DELETE'])
def remindersRemove(device):
	try:
		id = request.values["id"]
		reminder = Reminder.query.filter_by(device=device).filter_by(id=id).first()
		if reminder == None:
			return "0"
		else:
			db.session.delete(reminder)
			db.session.commit()
			return "1"
	except Exception as e:
		return "-1"

# Departures

@app.route('/departures/<stopCode>', methods=['GET'])
def getDepartures(stopCode):
	key = request.values.get("key")
	if key == None:
		return jsonify({"error": "No key was provided"})
	warningMode = True # Should be True on emergency cases only.
	r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetNextDepartures.json', params = {'key':key, 'stopCode': stopCode})
	tree = []
	try:
		if r.json()["errorCode"] == 500:
			return jsonify({"error": "tpg server unavailable"})
	except:
		pass
	for departure in r.json()["departures"]:
		if departure["waitingTime"] != "no more":
			a = {
				'line': {
					'lineCode': departure["line"]["lineCode"],
					'destinationName': departure["line"]["destinationName"],
					'destinationCode': departure["line"]["destinationCode"]
				},
				'departureCode': departure.get("departureCode", -1),
				'leftTime': departure.get("waitingTime", ""),
				'timestamp': departure.get("timestamp", ""),
				'vehiculeNo': departure.get("vehiculeNo", -1),
				'reliability': departure.get("reliability", ""),
				'characteristics': departure.get("characteristics", ""),
				'platform': None,
				'wifi': False,
				'operator': "tpg"
			}
			if 781 <= a["vehiculeNo"] <= 790:
				a["wifi"] = True
			elif 1601 <= a["vehiculeNo"] <= 1663:
				a["wifi"] = True
			elif 1271 <= a["vehiculeNo"] <= 1283:
				a["wifi"] = True
			try:
				a["timestampInt"] = int(dateutil.parser.parse(a["timestamp"]).strftime("%s"))
			except:
				pass
			if stopCode == "PRBE" and departure["line"]["lineCode"] == "14":
				r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json', params = {'key':key, 'departureCode': departure["departureCode"]})
				j = r.json()
				try:
					if j["steps"][0]["physicalStop"]["physicalStopCode"] == "PRBE01":
						a["platform"] = "1"
					elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "PRBE02":
						a["platform"] = "2"
				except:
					pass
			elif stopCode == "PALE" and (departure["line"]["lineCode"] == "12" or departure["line"]["lineCode"] == "15" or departure["line"]["lineCode"] == "14"):
				r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json', params = {'key':key, 'departureCode': departure["departureCode"]})
				j = r.json()
				try:
					if j["steps"][0]["physicalStop"]["physicalStopCode"] == "PALE01":
						a["platform"] = "1"
					elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "PALE02":
						a["platform"] = "2"
					elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "PALE03":
						a["platform"] = "2"
				except:
					pass
			elif stopCode == "GRVI" and departure["line"]["lineCode"] == "14":
				r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json', params = {'key':key, 'departureCode': departure["departureCode"]})
				j = r.json()
				try:
					if j["steps"][0]["physicalStop"]["physicalStopCode"] == "GRVI01":
						a["platform"] = "1"
					elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "GRVI02":
						a["platform"] = "2"
				except:
					pass
			elif stopCode == "NATI" and departure["line"]["lineCode"] == "15":
				r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json', params = {'key':key, 'departureCode': departure["departureCode"]})
				j = r.json()
				try:
					if j["steps"][0]["physicalStop"]["physicalStopCode"] == "NATI01":
						a["platform"] = "1"
					elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "NATI02":
						a["platform"] = "2"
				except:
					pass
			elif stopCode == "MOIL" and departure["line"]["lineCode"] == "12":
				r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json', params = {'key':key, 'departureCode': departure["departureCode"]})
				j = r.json()
				try:
					if j["steps"][0]["physicalStop"]["physicalStopCode"] == "MOIL01":
						a["platform"] = "1"
					elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "MOIL02":
						a["platform"] = "2"
				except:
					pass
			elif stopCode == "BHET" and (departure["line"]["lineCode"] == "12" or departure["line"]["lineCode"] == "18"):
				r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json', params = {'key':key, 'departureCode': departure["departureCode"]})
				j = r.json()
				try:
					d3 = [v for v in j["steps"] if v["stop"]["stopCode"] == "BHET"]
					if d3[0]["physicalStop"]["physicalStopCode"] == "BHET08":
						a["platform"] = "1"
					elif d3[0]["physicalStop"]["physicalStopCode"] == "BHET00":
						a["platform"] = "2"
					elif d3[0]["physicalStop"]["physicalStopCode"] == "BHET01":
						a["platform"] = "3"
				except:
					pass
			tree.append(a)
		else:
			a = {
				'line': {
					'lineCode': departure["line"]["lineCode"],
					'destinationName': departure["line"]["destinationName"],
					'destinationCode': departure["line"]["destinationCode"]
				},
				'waitingTime': departure["waitingTime"],
			}
			tree.append(a)
	try:
		stop = [x for x in stops if x["code"] == stopCode][0]
		sbbId = stop["sbbId"]
		if "tac" in stop["lines"].values():
			day = datetime.now().strftime("%a")
			if day == "Fri":
				stopDepartures = json.loads(departures["VEN" + str(sbbId) + ".json"])["departures"]
			elif day == "Sat":
				stopDepartures = json.loads(departures["SAM" + str(sbbId) + ".json"])["departures"]
			elif day == "Sun":
				stopDepartures = json.loads(departures["DIM" + str(sbbId) + ".json"])["departures"]
			else:
				stopDepartures = json.loads(departures["LUN" + str(sbbId) + ".json"])["departures"]

			lines = [x for x, y in stop["lines"].items() if y == "tac"]
			for x in tree:
				if x["line"]["lineCode"] in lines:
					tree.remove(x)
			for stopDeparture in stopDepartures:
				timestamp = int(dateutil.parser.parse(datetime.now().isoformat()[:10] + stopDeparture["timestamp"][10:]).strftime("%s"))
				nowTimestamp = int(datetime.now().strftime("%s"))
				if nowTimestamp <= timestamp <= (nowTimestamp + 3600):
					if stopDeparture["line"] in lines:
						try:
							destination = [x for x in stops if x["sbbId"] == stopDeparture["direction"]][0]["name"]
							tree.append({
								'line': {
								'lineCode': stopDeparture["line"],
								'destinationName': destination,
								'destinationCode': ""
								},
								'departureCode': -1,
								'leftTime': str(round((timestamp - nowTimestamp) / 60)),
								'timestamp': stopDeparture["timestamp"],
								'vehiculeNo': -1,
								'reliability': "T",
								'characteristics': "PMR",
								'platform': None,
								'wifi': False,
								'operator': "tac"
							})
						except:
							pass
			try:
				tree = sorted([x for x in tree if x["leftTime"].isdigit()], key=lambda item: int(item["leftTime"]))
			except:
				pass
			if warningMode:
				return jsonify({"departures": tree, "warning": "Public tpg api may have some troubles at this time. Please, do not rely on these departures times"})
			else:
				return jsonify({"departures": tree})
		else:
			if warningMode:
				return jsonify({"departures": tree, "warning": "Public tpg api may have some troubles at this time. Please, do not rely on these departures times"})
			else:
				return jsonify({"departures": tree})
	except Exception as e:
		raise e
		if warningMode:
			return jsonify({"departures": tree, "warning": "Public tpg api may have some troubles at this time. Please, do not rely on these departures times"})
		else:
			return jsonify({"departures": tree})

@app.route('/disruptions', methods=['GET'])
def getDisruptions():
	key = request.values.get("key")
	if key == None:
		return jsonify({"error": "No key was provided"})
	r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetDisruptions.json', params = {'key':key})
	try:
		if r.json()["errorCode"] == 500:
			return jsonify({"error": "tpg server unavailable"})
	except:
		pass
	a = r.json()
	for disruption in a["disruptions"]:
		if disruption["nature"][0] == " ":
			disruption["nature"] = disruption["nature"][1:]
		if disruption["nature"][-2:] == "\n\n":
			disruption["nature"] = disruption["nature"][:-2]
		if disruption["nature"][-1:] == "\n":
			disruption["nature"] = disruption["nature"][:-1]
		if disruption["nature"][-2:] == "\r\r":
			disruption["nature"] = disruption["nature"][:-2]
		if disruption["nature"][-1:] == "\r":
			disruption["nature"] = disruption["nature"][:-1]
		if disruption["consequence"][0] == " ":
			disruption["consequence"] = disruption["consequence"][1:]
		if disruption["consequence"][-2:] == "\n\n":
			disruption["consequence"] = disruption["consequence"][:-2]
		if disruption["consequence"][-1:] == "\n":
			disruption["consequence"] = disruption["consequence"][:-1]
		if disruption["consequence"][-2:] == "\r\r":
			disruption["consequence"] = disruption["consequence"][:-2]
		if disruption["consequence"][-1:] == "\r":
			disruption["consequence"] = disruption["consequence"][:-1]
		try:
			if disruption["place"][0] == " ":
				disruption["place"] = disruption["place"][1:]
			if disruption["place"][-2:] == "\n\n":
				disruption["place"] = disruption["place"][:-2]
			if disruption["place"][-1:] == "\n":
				disruption["place"] = disruption["place"][:-1]
			if disruption["place"][-2:] == "\r\r":
				disruption["place"] = disruption["place"][:-2]
			if disruption["place"][-1:] == "\r":
				disruption["place"] = disruption["place"][:-1]
		except:
			pass
	return jsonify(a)


