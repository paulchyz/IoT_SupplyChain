from flask import Flask, render_template,json,request,jsonify
from jinja2 import Template
import csv, json, ast
import os, sys
import requests

app = Flask(__name__)
currentPath = os.path.dirname(__file__)
configFile = os.path.join(currentPath,'config.json')
iotCSVfile = os.path.join(currentPath,'dataFiles/iotData.csv')
nfcCSVfile = os.path.join(currentPath,'dataFiles/nfcData.csv')
iotJSONfile = os.path.join(currentPath,'dataFiles/iotOutput.json')
nfcJSONfile = os.path.join(currentPath,'dataFiles/nfcOutput.json')
bcJSONfile = os.path.join(currentPath,'dataFiles/bcOutput.json')

# Set authorization parameters from config file
with open(configFile) as config:
    configVals = json.load(config)
    username = configVals['username']
    password = configVals['password']

# Create list of lists containing data from CSV data
def getCSV(filename, datatype):
    # Set table headers
    if datatype=='iot':
        CSVlist = [['Date', 'Time', 'Temperature', 'Humidity', 'Light', 'DateTime']]
    elif datatype=='nfc':
        CSVlist = [['ID', 'Date Hatched', 'Latitude', 'Longitude', 'Date', 'Time', 'DateTime']]
    else:
        CSVlist = [[]]

    if os.path.isfile(filename):
        # Store CSV data into list of lists
        with open(filename) as f:
            csvreader = csv.reader(f)
            count = 0
            for row in csvreader:
                if count > 0:
                    CSVlist.append(row)
                count += 1
    return CSVlist

# Return json data from IoT CSV
def makeIOTjson():
    # Copy CSV data to json file, also return json object
    if os.path.isfile(iotCSVfile):
        with open(iotCSVfile) as iotCsvFile:
            iotJson = open(iotJSONfile, 'w')
            iotreader = csv.DictReader(iotCsvFile)
            data = [r for r in iotreader]
            json.dump(data, iotJson)
    else:
        data = {"Date": "", "DateTime": "", "Humidity": "", "Light": "", "Temperature": "", "Time": ""}
    return jsonify(data)

# Return json data from NFC CSV
def makeNFCjson():
    # Copy CSV data to json file, also return json object
    if os.path.isfile(nfcCSVfile):
        with open(nfcCSVfile) as nfcCsvFile:
            nfcJson = open(nfcJSONfile, 'w')
            nfcreader = csv.DictReader(nfcCsvFile)

            data = [r for r in nfcreader]
            json.dump(data, nfcJson)
    else:
        data = {"Date": "", "Date Hatched": "", "DateTime": "", "ID": "", "Latitude": "", "Longitude": "", "Time": ""}
    return jsonify(data)

# Return json data from blockchain
def makeBCjson():
    # Post request to return blockchain data
    content = {"channel": "default", "chaincode": "obcs-cardealer", "method": "queryVehiclePartByOwner", "args": ["TysonFarms"], "chaincodeVer": "1.0"}
    data = requests.post(r'https://cloudforcebcmanager-gse00015180.blockchain.ocp.oraclecloud.com/restproxy1/bcsgw/rest/v1/transaction/query', json=content, auth=(username, password))

    # Parse blockchain data, store to json file, and return json object
    result = data.json()['result']
    encode = result['encode']
    payload = ast.literal_eval(result['payload'])

    # Write json to file
    with open(bcJSONfile, 'w') as jsonFile:
        jsonFile.write('[')
        for num, value in enumerate(payload):
            if num == 0:
                jsonFile.write(value['valueJson'])
            else:
                jsonFile.write(', ' + value['valueJson'])
        jsonFile.write(']')

    # Return final json
    with open(bcJSONfile, 'r') as jsonFile:
        data = json.load(jsonFile)
    return jsonify(data)

# Add newly posted data to NFC CSV file
def makeNFCcsv(nfcPost):
    # Make CSV and add headers if file does not exist
    if not os.path.isfile(nfcCSVfile):
        f = open(nfcCSVfile, 'w')
        fWriter = csv.writer(f)
        fWriter.writerow(['ID', 'Date Hatched', 'Latitude', 'Longitude', 'Date', 'Time', 'DateTime'])
        f.close()

    # Write data values to CSV file
    with open(nfcCSVfile, 'a') as dataFile:
        dateTime = nfcPost['Date'] + nfcPost['Time']
        dateTime = dateTime.replace('/', '')
        dateTime = dateTime.replace(':', '')

        fWriter = csv.writer(dataFile)
        fWriter.writerow([nfcPost['ID'], nfcPost['Date Hatched'], nfcPost['Latitude'], nfcPost['Longitude'], nfcPost['Date'], nfcPost['Time'], dateTime])
    return

# Add data to blockchain
def BCadd(nfcPost):
    dateTime = nfcPost['Date'] + nfcPost['Time']
    dateTime = dateTime.replace('/', '')
    dateTime = dateTime.replace(':', '')
    data = [nfcPost['ID'], 'Farm2', dateTime, 'TysonFarms', 'TysonFarms', 'false', '0']
    content = {"channel": "default","chaincode": "obcs-cardealer","method": "initVehiclePart","chaincodeVer": "1.0","args": data,"proposalWaitTime": 50000,"transactionWaitTime": 60000}
    resp = requests.post(r'https://cloudforcebcmanager-gse00015180.blockchain.ocp.oraclecloud.com:443/restproxy1/bcsgw/rest/v1/transaction/invocation', json=content, auth=(username, password))
    return

# Default testing display
@app.route("/")
def testView():
    # Pass CSV data as list of lists to index.html
    iotTable = getCSV(iotCSVfile, 'iot')
    nfcTable = getCSV(nfcCSVfile, 'nfc')
    return render_template('index.html', iotTable=iotTable, nfcTable=nfcTable)

# Return all IoT data as json
@app.route("/iot")
def iotAllOut():
    # Get iot json string from CSV and return it
    IOTjson = makeIOTjson()
    return IOTjson

# Return all NFC data as json
@app.route("/nfc")
def nfcAllOut():
    # Get nfc json string from CSV and return it
    NFCjson = makeNFCjson()
    return NFCjson    

# Return all blockchain data as json
@app.route("/blockchain")
def bcAllOut():
    # Get nfc json string from CSV and return it
    BCjson = makeBCjson()
    return BCjson 

# Add NFC data to system when posted in json format
@app.route('/postjson', methods = ['POST'])
def receivePost():
    # Get json data and send to CSV file
    message = request.get_json()
    makeNFCcsv(message)
    BCadd(message)
    return 'JSON posted'

# Add NFC data to system when posted from phone app
@app.route('/post', methods = ['POST'])
def postJsonHandler():
    message = request.form
    makeNFCcsv(message)
    BCadd(message)
    return 'JSON posted'

# Test route with ID number
@app.route('/nfc/<nfcid>')
def api_article(nfcid):
    return 'You are reading ' + nfcid

# Delete all CSV and json files in dataFiles directory
@app.route("/deleteall")
def deleteAll():
    if os.path.isfile(iotCSVfile):
        os.remove(iotCSVfile)
    if os.path.isfile(nfcCSVfile):
        os.remove(nfcCSVfile)
    if os.path.isfile(iotJSONfile):
        os.remove(iotJSONfile)
    if os.path.isfile(nfcJSONfile):
        os.remove(nfcJSONfile)
    if os.path.isfile(bcJSONfile):
        os.remove(bcJSONfile)
    return 'All Data Files Deleted'

# Delete IoT CSV and json files in dataFiles directory
@app.route("/deleteiot")
def deleteIOT():
    if os.path.isfile(iotCSVfile):
        os.remove(iotCSVfile)
    if os.path.isfile(iotJSONfile):
        os.remove(iotJSONfile)
    return 'IoT Data Files Deleted'

# Delete NFC CSV and json files in dataFiles directory
@app.route("/deletenfc")
def deleteNFC():
    if os.path.isfile(nfcCSVfile):
        os.remove(nfcCSVfile)
    if os.path.isfile(nfcJSONfile):
        os.remove(nfcJSONfile)
    return 'NFC Data Files Deleted'

# Delete blockchain CSV and json files in dataFiles directory
@app.route("/deleteblockchain")
def deleteBC():
    if os.path.isfile(bcJSONfile):
        os.remove(bcJSONfile)
    return 'Blockchain Data Files Deleted'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
