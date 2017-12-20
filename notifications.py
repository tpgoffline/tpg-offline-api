from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert
import pymysql
import requests
from datetime import datetime
import json

connection = pymysql.connect(host='host',
							 user='user',
							 password='password',
							 db='tpgoffline-apns_apns',
							 charset='utf8mb4',
							 cursorclass=pymysql.cursors.DictCursor)

r = requests.get('http://prod.ivtr-od.tpg.ch/v1/GetDisruptions.json', params = {'key':'key'})
j = r.json()
k = json.loads(open("lastSeenDisruptions.json", "r").read())

for disruption in j["disruptions"]:
	if disruption not in k:
		try:
			with connection.cursor() as cursor:
				# Read a single record
				sql = "SELECT * FROM `user` WHERE `line`=%s"
				cursor.execute(sql, (disruption["lineCode"],))
				for row in cursor.fetchall():
					today = datetime.today()
					fromHourVar = datetime.strptime(row["fromHour"], "%H:%M")
					fromHour = today.replace(hour=fromHourVar.hour, minute=fromHourVar.minute, second=0, microsecond=0)
					toHourVar = datetime.strptime(row["toHour"], "%H:%M")
					toHour = today.replace(hour=toHourVar.hour, minute=toHourVar.minute, second=0, microsecond=0)
					days = list(map(int, row["days"].split(":")))
					if fromHour < today < toHour and today.weekday() in days:
						token_hex = row["device"]
						if row["language"] == "fr":
							payload = Payload(alert=PayloadAlert(title="Perturbation en cours", body= f"Ligne {disruption['lineCode']} - {disruption['consequence']}"), sound="default", badge=0)
						else:
							payload = Payload(alert=PayloadAlert(title="Disruption ongoing", body= f"Line {disruption['lineCode']} - {disruption['consequence']}"), sound="default", badge=0)
						topic = 'com.dacostafaro.tpgoffline'
						client = APNsClient('key.pem', use_sandbox=False, use_alternative_port=False)
						client.send_notification(token_hex, payload, topic)

						sql = "INSERT INTO `notifications_sent` (`device`, `line`, `date`, `hour`, `text`) VALUES (%s, %s, %s, %s, %s)"
						cursor.execute(sql, (row["device"], disruption['lineCode'], f"{today.day}/{today.month}/{today.year}", f"{today.hour}:{today.minute}", disruption['consequence']))
						connection.commit()
					else:
						print("No")
		finally:
			pass

open("lastSeenDisruptions.json", "w").write(json.dumps(j["disruptions"], ensure_ascii=False))
connection.close()
