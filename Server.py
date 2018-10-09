from flask import Flask, render_template,json,request,jsonify
from jinja2 import Template
import csv, json, ast
import os, sys
import requests

app = Flask(__name__)
currentPath = os.path.dirname(__file__)
print(currentPath)
configFile = os.path.join(currentPath,'config.json')
iotCSVfile = os.path.join(currentPath,'dataFiles/iotData.csv')
nfcCSVfile = os.path.join(currentPath,'dataFiles/nfcData.csv')
iotJSONfile = os.path.join(currentPath,'dataFiles/iotOutput.json')
nfcJSONfile = os.path.join(currentPath,'dataFiles/nfcOutput.json')
bcJSONfile = os.path.join(currentPath,'dataFiles/bcOutput.json')
bcTestFile = os.path.join(currentPath,'dataFiles/data.json')

with open(configFile) as config:
    configVals = json.load(config)
    username = configVals['username']
    password = configVals['password']


def getCSV(filename, datatype):
    # Set table headers
    if datatype=='iot':
        CSVlist = [['Date', 'Time', 'Temperature', 'Humidity', 'Light', 'DateTime']]
    elif datatype=='nfc':
        CSVlist = [['ID', 'Date Hatched', 'Latitude', 'Longitude', 'Date', 'Time', 'DateTime']]
    else:
        CSVlist = [[]]

    # Store CSV data into list of lists
    with open(filename) as f:
        csvreader = csv.reader(f)
        count = 0
        for row in csvreader:
            if count > 0:
                CSVlist.append(row)
            count += 1
    return CSVlist

def makeIOTjson():
    # Copy CSV data to json file, also return json object
    with open(iotCSVfile) as iotCsvFile:
        iotJson = open(iotJSONfile, 'w')
        iotreader = csv.DictReader(iotCsvFile)
        data = [r for r in iotreader]
        json.dump(data, iotJson)
    return jsonify(data)

def makeNFCjson():
    # Copy CSV data to json file, also return json object
    with open(nfcCSVfile) as nfcCsvFile:
        nfcJson = open(nfcJSONfile, 'w')
        nfcreader = csv.DictReader(nfcCsvFile)

        data = [r for r in nfcreader]
        json.dump(data, nfcJson)
    return jsonify(data)

def makeBCjson():
    # Post request to return blockchain data
    content = {"channel": "default", "chaincode": "obcs-cardealer", "method": "queryVehiclePartByOwner", "args": ["TysonFarms"], "chaincodeVer": "1.0"}
    data = requests.post(r'https://cloudforcebcmanager-gse00015180.blockchain.ocp.oraclecloud.com/restproxy1/bcsgw/rest/v1/transaction/query', json=content, auth=(username, password))

    # Parse blockchain data, store to json file, and return json object
    result = data.json()['result']
    encode = result['encode']
    payload = ast.literal_eval(result['payload'])
    print (payload)

    with open(bcJSONfile, 'w') as jsonFile:
        jsonFile.write('[')
        for num, value in enumerate(payload):
            if num == 0:
                jsonFile.write(value['valueJson'])
            else:
                jsonFile.write(', ' + value['valueJson'])
        jsonFile.write(']')

    with open(bcJSONfile, 'r') as jsonFile:
        data = json.load(jsonFile)
    return jsonify(data)

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

def BCadd(nfcPost):
    dateTime = nfcPost['Date'] + nfcPost['Time']
    dateTime = dateTime.replace('/', '')
    dateTime = dateTime.replace(':', '')
    data = [nfcPost['ID'], 'Farm2', dateTime, 'TysonFarms', 'TysonFarms', 'false', '0']
    content = {"channel": "default","chaincode": "obcs-cardealer","method": "initVehiclePart","chaincodeVer": "1.0","args": data,"proposalWaitTime": 50000,"transactionWaitTime": 60000}
    resp = requests.post(r'https://cloudforcebcmanager-gse00015180.blockchain.ocp.oraclecloud.com:443/restproxy1/bcsgw/rest/v1/transaction/invocation', json=content, auth=(username, password))
    return

@app.route("/")
def testView():
    # Pass CSV data as list of lists to index.html
    iotTable = getCSV(iotCSVfile, 'iot')
    nfcTable = getCSV(nfcCSVfile, 'nfc')
    return render_template('index.html', iotTable=iotTable, nfcTable=nfcTable)

@app.route("/iot")
def iotAllOut():
    # Get iot json string from CSV and return it
    IOTjson = makeIOTjson()
    return IOTjson

@app.route("/nfc")
def nfcAllOut():
    # Get nfc json string from CSV and return it
    NFCjson = makeNFCjson()
    return NFCjson    

@app.route('/postjson', methods = ['POST'])
def receivePost():
    # Get json data and send to CSV file
    message = request.get_json()
    makeNFCcsv(message)
    BCadd(message)
    return 'JSON posted'

@app.route('/nfc/<nfcid>')
def api_article(nfcid):
    return 'You are reading ' + nfcid

@app.route('/post', methods = ['POST'])
def postJsonHandler():
    message = request.form
    makeNFCcsv(message) 
    return 'JSON posted'

@app.route("/blockchain")
def bcAllOut():
    # Get nfc json string from CSV and return it
    BCjson = makeBCjson()
    return BCjson 

#test json to be sent
#     { "device":"TemperatureSensor", 
#  "value":"20", 
#  "timestamp":"25/01/2017 10:10:05" 
# }


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
