from flask import Flask, render_template
from jinja2 import Template
import csv

app = Flask(__name__)
path = r'/Users/pchyz/Documents/AppDev/Capstone/data.csv'

@app.route("/")
def main():
    # Set table to headers
    table = [['yr/mo/d', 'time', 'temperature', 'humidity', 'light']]

    # Store CSV data into list of lists
    with open(path) as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            if count > 0:
                table.append(row)
            count += 1

    # Generate HTML
    return render_template('index.html', table=table)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)