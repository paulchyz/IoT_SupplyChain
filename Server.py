from flask import Flask, render_template,json,request
from jinja2 import Template
import csv, json
import os

app = Flask(__name__)
iotCSVfile = r'iotData.csv'
nfcCSVfile = r'nfcData.csv'
iotJSONfile = r'iotOutput.json'
nfcJSONfile = r'nfcOutput.json'

def getCSV(filename, datatype):
    # Set table headers
    if datatype=='iot':
        CSVlist = [['Date', 'Time', 'Temperature', 'Humidity', 'Light']]
    elif datatype=='nfc':
        CSVlist = [['ID', 'Date Hatched', 'Longitude', 'Latitude', 'Time']]
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
    # Copy CSV data to json file and store in list
    with open(iotCSVfile) as iotCsvFile:
        iotJson = open(iotJSONfile, 'w')
        iotreader = csv.DictReader(iotCsvFile)
        
        data = [r for r in iotreader]
        json.dump(data, iotJson)
        iotJsonOut = json.dumps(data)
    return iotJsonOut

def makeNFCjson():
    # Copy CSV data to json file and store in list
    with open(nfcCSVfile) as nfcCsvFile:
        nfcJson = open(nfcJSONfile, 'w')
        nfcreader = csv.DictReader(nfcCsvFile)

        data = [r for r in nfcreader]
        json.dump(data, nfcJson)
        nfcJsonOut = json.dumps(data)
    return nfcJsonOut

def makeNFCcsv(nfcPost):
    # Make CSV and add headers if file does not exist
    if not os.path.isfile(nfcCSVfile):
        f = open(nfcCSVfile, 'w')
        fWriter = csv.writer(f)
        fWriter.writerow(['ID', 'Date Hatched', 'Latitude', 'Longitude', 'Time'])
        f.close()

    # Write data values to CSV file
    with open(nfcCSVfile, 'a') as dataFile:
        fWriter = csv.writer(dataFile)
        fWriter.writerow([nfcPost['ID'], nfcPost['Date Hatched'], nfcPost['Latitude'], nfcPost['Longitude'], nfcPost['Time']])
    return

@app.route("/testview")
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

@app.route('/post', methods = ['POST'])
def receivePost():
    # Get json data and send to CSV file
    message = request.get_json()
    output = makeNFCcsv(message)
    return 'JSON posted'

@app.route('/nfc/<nfcid>')
def api_article(nfcid):
    return 'You are reading ' + nfcid

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    content = request.get_json()
    print (content)
    return 'JSON posted'

#test json to be sent
#     { "device":"TemperatureSensor", 
#  "value":"20", 
#  "timestamp":"25/01/2017 10:10:05" 
# }


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)