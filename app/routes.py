from app import app
from flask import jsonify, redirect
from flask import request, abort, render_template
import requests
import json
from datetime import datetime, timedelta
import dateutil.parser
import requests
from tpgroutes import TpgRoutes

stops = requests.get(
    "https://raw.githubusercontent.com/tpgoffline/tpgoffline-data/master/stops.json"
).json()
departures = requests.get(
    "https://raw.githubusercontent.com/tpgoffline/tpgoffline-data/master/departures.json"
).json()
tpgRoutes = TpgRoutes(logger=app.logger)


@app.route("/")
def index():
    return render_template("index.html")


# Departures


@app.route("/departures/<stopCode>", methods=["GET"])
def getDepartures(stopCode):
    key = request.values.get("key")
    if key == None:
        return jsonify({"error": "No key was provided"})
    r = requests.get(
        "http://prod.ivtr-od.tpg.ch/v1/GetNextDepartures.json",
        params={"key": key, "stopCode": stopCode},
    )
    tree = []
    try:
        if r.json()["errorCode"] == 500:
            return jsonify({"error": "tpg server unavailable"}), 500
    except:
        pass
    for departure in r.json()["departures"]:
        if departure["waitingTime"] != "no more":
            a = {
                "line": {
                    "lineCode": departure["line"]["lineCode"],
                    "destinationName": departure["line"]["destinationName"],
                    "destinationCode": departure["line"]["destinationCode"],
                },
                "departureCode": departure.get("departureCode", -1),
                "leftTime": departure.get("waitingTime", ""),
                "timestamp": departure.get("timestamp", ""),
                "vehiculeNo": departure.get("vehiculeNo", -1),
                "reliability": departure.get("reliability", ""),
                "characteristics": departure.get("characteristics", ""),
                "platform": None,
                "wifi": False,
                "operator": "tpg",
            }
            if 781 <= a["vehiculeNo"] <= 790:
                a["wifi"] = True
            elif 1601 <= a["vehiculeNo"] <= 1663:
                a["wifi"] = True
            elif 1271 <= a["vehiculeNo"] <= 1283:
                a["wifi"] = True
            try:
                a["timestampInt"] = int(
                    dateutil.parser.parse(a["timestamp"]).strftime("%s")
                )
            except:
                pass
            if stopCode == "PRBE" and departure["line"]["lineCode"] == "14":
                r = requests.get(
                    "http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json",
                    params={"key": key, "departureCode": departure["departureCode"]},
                )
                j = r.json()
                try:
                    if j["steps"][0]["physicalStop"]["physicalStopCode"] == "PRBE01":
                        a["platform"] = "1"
                    elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "PRBE02":
                        a["platform"] = "2"
                except:
                    pass
            elif stopCode == "PALE" and (
                departure["line"]["lineCode"] == "12"
                or departure["line"]["lineCode"] == "15"
                or departure["line"]["lineCode"] == "14"
            ):
                r = requests.get(
                    "http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json",
                    params={"key": key, "departureCode": departure["departureCode"]},
                )
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
                r = requests.get(
                    "http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json",
                    params={"key": key, "departureCode": departure["departureCode"]},
                )
                j = r.json()
                try:
                    if j["steps"][0]["physicalStop"]["physicalStopCode"] == "GRVI01":
                        a["platform"] = "1"
                    elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "GRVI02":
                        a["platform"] = "2"
                except:
                    pass
            elif stopCode == "NATI" and departure["line"]["lineCode"] == "15":
                r = requests.get(
                    "http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json",
                    params={"key": key, "departureCode": departure["departureCode"]},
                )
                j = r.json()
                try:
                    if j["steps"][0]["physicalStop"]["physicalStopCode"] == "NATI01":
                        a["platform"] = "1"
                    elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "NATI02":
                        a["platform"] = "2"
                except:
                    pass
            elif stopCode == "MOIL" and departure["line"]["lineCode"] == "12":
                r = requests.get(
                    "http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json",
                    params={"key": key, "departureCode": departure["departureCode"]},
                )
                j = r.json()
                try:
                    if j["steps"][0]["physicalStop"]["physicalStopCode"] == "MOIL01":
                        a["platform"] = "1"
                    elif j["steps"][0]["physicalStop"]["physicalStopCode"] == "MOIL02":
                        a["platform"] = "2"
                except:
                    pass
            elif stopCode == "BHET" and (
                departure["line"]["lineCode"] == "12"
                or departure["line"]["lineCode"] == "18"
            ):
                r = requests.get(
                    "http://prod.ivtr-od.tpg.ch/v1/GetThermometerPhysicalStops.json",
                    params={"key": key, "departureCode": departure["departureCode"]},
                )
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
                "line": {
                    "lineCode": departure["line"]["lineCode"],
                    "destinationName": departure["line"]["destinationName"],
                    "destinationCode": departure["line"]["destinationCode"],
                },
                "waitingTime": departure["waitingTime"],
            }
            tree.append(a)
    try:
        stop = [x for x in stops if x["code"] == stopCode][0]
        sbbId = stop["sbbId"]
        if "tac" in stop["lines"].values():
            day = datetime.now().strftime("%a")
            if day == "Fri":
                stopDepartures = json.loads(departures["VEN" + str(sbbId) + ".json"])[
                    "departures"
                ]
            elif day == "Sat":
                stopDepartures = json.loads(departures["SAM" + str(sbbId) + ".json"])[
                    "departures"
                ]
            elif day == "Sun":
                stopDepartures = json.loads(departures["DIM" + str(sbbId) + ".json"])[
                    "departures"
                ]
            else:
                stopDepartures = json.loads(departures["LUN" + str(sbbId) + ".json"])[
                    "departures"
                ]

            lines = [x for x, y in stop["lines"].items() if y == "tac"]
            for x in tree:
                if x["line"]["lineCode"] in lines:
                    tree.remove(x)
            for stopDeparture in stopDepartures:
                timestamp = int(
                    dateutil.parser.parse(
                        datetime.now().isoformat()[:10]
                        + stopDeparture["timestamp"][10:]
                    ).strftime("%s")
                )
                nowTimestamp = int(datetime.now().strftime("%s"))
                if nowTimestamp <= timestamp <= (nowTimestamp + 3600):
                    if stopDeparture["line"] in lines:
                        try:
                            destination = [
                                x
                                for x in stops
                                if x["sbbId"] == stopDeparture["direction"]
                            ][0]["name"]
                            tree.append(
                                {
                                    "line": {
                                        "lineCode": stopDeparture["line"],
                                        "destinationName": destination,
                                        "destinationCode": "",
                                    },
                                    "departureCode": -1,
                                    "leftTime": str(
                                        round((timestamp - nowTimestamp) / 60)
                                    ),
                                    "timestamp": stopDeparture["timestamp"],
                                    "vehiculeNo": -1,
                                    "reliability": "T",
                                    "characteristics": "PMR",
                                    "platform": None,
                                    "wifi": False,
                                    "operator": "tac",
                                }
                            )
                        except:
                            pass
            try:
                tree = sorted(
                    [x for x in tree if x["leftTime"].isdigit()],
                    key=lambda item: int(item["leftTime"]),
                )
            except:
                pass
            return jsonify({"departures": tree})
        else:
            return jsonify({"departures": tree})
    except:
        return jsonify({"departures": tree})


@app.route("/disruptions", methods=["GET"])
def getDisruptions():
    key = request.values.get("key")
    if key == None:
        return jsonify({"error": "No key was provided"}), 400
    r = requests.get(
        "http://prod.ivtr-od.tpg.ch/v1/GetDisruptions.json", params={"key": key}
    )
    try:
        if r.json()["errorCode"] == 500:
            return jsonify({"error": "tpg server unavailable"}), 400
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


def getStopByString(string):
    try:
        assert type(string) == str
        stopsByCode = [x for x in app.stops if x["code"] == string]
        if len(stopsByCode) > 0:
            return stopsByCode[0]["sbbId"]
        stopsBySBBId = [x for x in app.stops if x["sbbId"] == string]
        if len(stopsBySBBId) > 0:
            return stopsBySBBId[0]["sbbId"]
        stopsByAppId = [x for x in app.stops if x["appId"] == string]
        if len(stopsByAppId) > 0:
            return stopsByAppId[0]["sbbId"]
        return None
    except:
        return None


@app.route("/routes", methods=["GET"])
def getRoutes():
    departureStop = getStopByString(request.values.get("departureStop"))
    arrivalStop = getStopByString(request.values.get("arrivalStop"))
    departureTime = request.values.get("arrivalStop")
    numberOfRoutes = request.values.get("numberOfRoutes")
    try:
        departureStop = int(departureStop)
    except:
        return jsonify({"error": "departureStop is incorrect"}), 400
    try:
        arrivalStop = int(arrivalStop)
    except:
        return jsonify({"error": "arrivalStop is incorrect"}), 400
    try:
        departureTime = dateutil.parser.parse(departureTime)
        departureSeconds = (
            departureTime
            - departureTime.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds()
        day = departureTime.weekday()
    except:
        return jsonify({"error": "departureTime is incorrect"}), 400
    try:
        numberOfRoutes = int(numberOfRoutes)
        assert 0 <= numberOfRoutes <= 6
    except:
        return jsonify({"error": "numberOfRoutes is incorrect"}), 400
    routes = []
    for x in range(6):
        route = tpgRoutes.compute_route(
            departureStop, arrivalStop, departureSeconds, day
        )
        routes.append(
            {
                "departureTime": (
                    departureTime.replace(hour=0, minute=0, second=0, microsecond=0)
                    + timedelta(seconds=route[0].departure_time)
                ).isoformat(),
                "arrivalTime": (
                    departureTime.replace(hour=0, minute=0, second=0, microsecond=0)
                    + timedelta(seconds=route[-1].arrivalTime)
                ).isoformat(),
                "path": [
                    {
                        "departureStop": y.departure_stop,
                        "arrivalStop": y.arrival_stop,
                        "departureTime": (
                            departureTime.replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )
                            + timedelta(seconds=y.departure_time)
                        ).isoformat(),
                        "arrivalTime": (
                            departureTime.replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )
                            + timedelta(seconds=y.arrival_time)
                        ).isoformat(),
                        "line": y.line,
                        "destination_stop": y.destination_stop,
                    }
                    for y in route
                ],
            }
        )
        departureTime = route[0].departure_time + 1
    return
