import requests, time, csv, os.path, sys, json

currentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
iotCSVfile = currentPath + r'/dataFiles/iotData.csv'
alertFile = currentPath + r'/dataFiles/alerts.json'
alertList = []

# Make CSV and add headers if file does not exist
if not os.path.isfile(iotCSVfile):
    f = open(iotCSVfile, 'w')
    fWriter = csv.writer(f)
    fWriter.writerow(['Date','Time','Temperature','Humidity','Light', 'DateTime'])
    f.close()

# Infinite loop
while True:
    
    # Get humidity
    humidity = requests.get(r'https://us.wio.seeed.io/v1/node/GroveTempHumD1/humidity?access_token=8ccf1ac10486e01c4651835f57265e91')
    humidityNum = humidity.json()['humidity']
    print('Humidity: ' + str(humidityNum))

    # Get light
    light = requests.get(r'https://us.wio.seeed.io/v1/node/GroveDigitalLightI2C0/lux?access_token=8ccf1ac10486e01c4651835f57265e91')
    lightNum = light.json()['lux']
    print('Light: ' + str(lightNum))

    # Get temp
    temp = requests.get(r'https://us.wio.seeed.io/v1/node/GroveTempHumD1/temperature_f?access_token=8ccf1ac10486e01c4651835f57265e91')
    tempNum = temp.json()['fahrenheit_degree']
    print('Temp: ' + str(tempNum))

    # Get date and time
    currentDate = time.strftime('%Y/%m/%d', time.gmtime())
    currentTime = time.strftime('%H:%M:%S', time.gmtime())
    dateTime = time.strftime('%Y%m%d%H%M%S', time.gmtime())

    tempFlag = 0
    if tempNum > 75:
        tempFlag = 1
    humFlag = 0
    if humidityNum > 52:
        humFlag = 1
    
    if not os.path.isfile(alertFile):
        f = open(alertFile, 'w')
        f.close()

    if tempFlag == 1 and humFlag == 1:
        message = {'Temperature_Alert': True, 'Humidity_Alert': True, 'Temperature': tempNum, 'Humidity': humidityNum, 'Light': lightNum, 'Date': currentDate, 'Time': currentTime, 'DateTime': dateTime}
        alertList.append(message)
    elif tempFlag == 1:
        message = {'Temperature_Alert': True, 'Humidity_Alert': False, 'Temperature': tempNum, 'Humidity': humidityNum, 'Light': lightNum, 'Date': currentDate, 'Time': currentTime, 'DateTime': dateTime}
        alertList.append(message)
    elif humFlag == 1:
        message = {'Temperature_Alert': False, 'Humidity_Alert': True, 'Temperature': tempNum, 'Humidity': humidityNum, 'Light': lightNum, 'Date': currentDate, 'Time': currentTime, 'DateTime': dateTime}
        alertList.append(message)
    
    with open(alertFile, 'w') as af:
        json.dump(alertList, af)

    # Append data to CSV
    with open(iotCSVfile, 'a') as dataFile:
        fWriter = csv.writer(dataFile)
        fWriter.writerow([currentDate, currentTime, tempNum, humidityNum, lightNum, dateTime])
    
    # Two-second intervals
    time.sleep(2)