from flask import Flask, render_template,json,request
from jinja2 import Template
import csv, json

app = Flask(__name__)
iotCSVfile = r'iotData.csv'
nfcCSVfile = r'nfcData.csv'
iotJSONfile = r'iotOutput.json'
nfcJSONfile = r'nfcOutput.json'

def getCSV():
    # Set table to headers
    CSVlist = [['Date (y/m/d)', 'Time', 'Temperature', 'Humidity', 'Light']]

    # Store CSV data into list of lists
    with open(iotCSVfile) as f:
        csvreader = csv.reader(f)
        count = 0
        for row in csvreader:
            if count > 0:
                CSVlist.append(row)
            count += 1
    return CSVlist

def getIOTjson():
    iotJsonList = []

    # Copy csv data to json file and store in list
    with open(iotCSVfile) as iotCsvFile:
        iotJson = open(iotJSONfile, 'w')
        iotreader = csv.DictReader(iotCsvFile)
        for row in iotreader:
            json.dump(row, iotJson)
            iotJson.write('\n')
            iotJsonList.append(json.dumps(row))

    # Convert json list to string for return value
    iotJsonOut = str(iotJsonList)
    iotJsonOut = iotJsonOut.replace("'","")
    iotJsonOut = iotJsonOut[1:-1]
    return iotJsonOut

def getNFCjson():
    nfcJsonList = []

    # Copy csv data to json file and store in list
    with open(nfcCSVfile) as nfcCsvFile:
        nfcJson = open(nfcJSONfile, 'w')
        nfcreader = csv.DictReader(nfcCsvFile)
        for row in nfcreader:
            json.dump(row, nfcJson)
            nfcJson.write('\n')
            nfcJsonList.append(json.dumps(row))

    # Convert json list to string for return value
    nfcJsonOut = str(nfcJsonList)
    nfcJsonOut = nfcJsonOut.replace("'","")
    nfcJsonOut = nfcJsonOut[1:-1]
    return nfcJsonOut

@app.route("/testview")
def testView():
    # Pass CSV data as list of lists to index.html
    table = getCSV()
    return render_template('index.html', table=table)

@app.route("/iot")
def iotAllOut():
    # Get iot json string and return it
    IOTjson = getIOTjson()
    return IOTjson

@app.route("/nfc")
def nfcAllOut():
    # Get nfc json string and return it
    NFCjson = getNFCjson()
    return NFCjson

@app.route('/nfc/<nfcid>')
def api_article(nfcid):
    return 'You are reading ' + nfcid
    

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    content = request.get_json()
    print (content)
    print(content["device"])
    
    return 'JSON posted'

#test json to be sent
#     { "device":"TemperatureSensor", 
#  "value":"20", 
#  "timestamp":"25/01/2017 10:10:05" 
# }


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)