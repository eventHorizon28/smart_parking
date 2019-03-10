from flask import Flask, jsonify, make_response, request
import smartcar
from car import auth

app=Flask(__name__)

client = smartcar.AuthClient(auth.client_id, auth.client_secret, auth.redirect_uri, auth.scope)
access = {}

@app.route('/access', methods=["GET"])
def index():
    auth_url = client.get_auth_url()
    return """
    <h1>Hello!</h1>
    <a href=%s>
        <button>Sign in to connect car</button>
    </a>
    """ %auth_url

@app.route('/', methods=["GET"])
def getAccess():
    code = request.args.get('code')
    
    global access
    access = client.exchange_code(code)
    return """
    <h1>Signed in!</h1>
    <a href="""+auth.redirect_uri+"/vehicles"+""">
        <button>Vehicles</button>
    </a>
    """
@app.route('/vehicles', methods=["GET"])
def allVehicles():
    global access
    print(access)
    vehicle_ids = smartcar.get_vehicle_ids(access['access_token'])['vehicles']
    print(vehicle_ids)
    
    vehicles = []

    for id in vehicle_ids:
        vehicles.append(smartcar.Vehicle(id, access['access_token']))

    str = ""
    for vehicle in vehicles:
        str += """
        <a href="""+auth.redirect_uri+"/vehicles/"+vehicle.info()["id"]+""">
            <button>"""+vehicle.info()["make"]+" "+vehicle.info()["model"]+"""</button>
        </a>
    """
    return str

@app.route('/vehicles/<vid>', methods=["GET"])
def vehicleInfo(vid):
    global access
    print(vid)

    vehicle = smartcar.Vehicle(vid, access['access_token'])
    response = "<p>"+str(vehicle.info()["make"])+"</p>"
    response += "<p>"+str(vehicle.info()["model"])+"</p>"
    print(response)
    response += "<p>"+str(vehicle.location()["data"]["latitude"])+", "+str(vehicle.location()["data"]["longitude"])+"</p>"
    
    response += """
        <a href = """+auth.redirect_uri+"/vehicles/"+vid+"""/parking>
            <button>find parking</button>
        </a>
        <a href = """+auth.redirect_uri+"/vehicles/"+vid+"""/lock>
            <button>lock</button>
        </a>
        <a href = """+auth.redirect_uri+"/vehicles/"+vid+"""/unlock>
            <button>unlock</button>
        </a>"""
    print(response)

    return response


@app.route('/vehicles/<vid>/parking', methods=["GET"])
def parking(vid):
    global access
    print(vid)

    vehicle = smartcar.Vehicle(vid, access['access_token'])
    
    
    return jsonify(vehicle.info())

@app.route('/vehicles/<vid>/lock', methods=["POST"])
def vehicleLock(vid):
    global access
    print(vid)

    vehicle = smartcar.Vehicle(vid, access['access_token'])
    value = vehicle.lock()
    if(value == True):
        return "locked"
    return "neh"

@app.route('/vehicles/<vid>/unlock', methods=["POST"])
def vehicleUnlock(vid):
    global access
    print(vid)

    vehicle = smartcar.Vehicle(vid, access['access_token'])
    value = vehicle.unlock()
    if(value == False):
        return "unlocked"
    return "neh"