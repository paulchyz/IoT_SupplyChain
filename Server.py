from flask import Flask, render_template,json,request
from jinja2 import Template
import csv, json

app = Flask(__name__)
iotCSVfile = r'iotData.csv'
nfcCSVfile = r'nfcData.csv'
iotJSONfile = r'jsonOutput.csv'
nfcJSONfile = r'jsonOutput.csv'

def getCSV():
    # Set table to headers
    CSVlist = [['Date (y/m/d)', 'Time', 'Temperature', 'Humidity', 'Light']]

    # Store CSV data into list of lists
    with open(iotCSVfile) as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            if count > 0:
                CSVlist.append(row)
            count += 1
    return CSVlist

def getIOTjson():
    jsonList = []

    # Copy csv data to json file and store in list
    with open(iotCSVfile) as csvFile:
        jsonFile = open(iotJSONfile, 'w')
        reader = csv.DictReader(csvFile)
        for row in reader:
            json.dump(row, jsonFile)
            jsonFile.write('\n')
            jsonList.append(json.dumps(row))

    # Convert json list to string for return value
    jsonOut = str(jsonList)
    jsonOut = jsonOut.replace("'","")
    jsonOut = jsonOut[1:-1]
    return jsonOut

@app.route("/testview")
def testView():
    # Pass CSV data as list of lists to index.html
    table = getCSV()
    return render_template('index.html', table=table)

@app.route("/iot")
def iotAllOut():
    # Get json string and return it
    IOTjson = getIOTjson()
    return IOTjson

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