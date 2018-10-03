from flask import Flask, render_template,json,request
from jinja2 import Template
import csv

app = Flask(__name__)
path = r'/Users/pchyz/Documents/GitHub/IoT_SupplyChain/data.csv'

def getCSV():
    # Set table to headers
    CSVlist = [['yr/mo/d', 'time', 'temperature', 'humidity', 'light']]

    # Store CSV data into list of lists
    with open(path) as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            if count > 0:
                CSVlist.append(row)
            count += 1
    return CSVlist

@app.route("/testview")
def testView():
    # Pass CSV data as list of lists to index.html
    table = getCSV()
    return render_template('index.html', table=table)

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