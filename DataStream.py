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

tempFlag = 0
humFlag = 0
alertFlag = 0

# Infinite loop
while True:
    
    # Get humidity
    humidity = requests.get(r'https://us.wio.seeed.io/v1/node/GroveTempHumD1/humidity?access_token=8ccf1ac10486e01c4651835f57265e91')
    humidityNum = humidity.json()['humidity']
    print('Humidity: ' + str(humidityNum))

    # Get light
    light = requests.get(r'https://us.wio.seeed.io/v1/node/GroveDigitalLightI2C0/lux?access_token=8ccf1ac10486e01c4651835f57265e91')
    if 'lux' in light.json():
        lightNum = light.json()['lux']
    else:
        lightNum = 999
    print('Light: ' + str(lightNum))

    # Get temp
    temp = requests.get(r'https://us.wio.seeed.io/v1/node/GroveTempHumD1/temperature_f?access_token=8ccf1ac10486e01c4651835f57265e91')
    tempNum = temp.json()['fahrenheit_degree']
    print('Temp: ' + str(tempNum))

    #humidityNum = 50
    #lightNum = 700
    #tempNum = 70

    # Get date and time
    currentDate = time.strftime('%Y/%m/%d', time.gmtime())
    currentTime = time.strftime('%H:%M:%S', time.gmtime())
    dateTime = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    
    if not os.path.isfile(alertFile):
        alertFlag = 0
    else:
        alertFlag = 2
    #    f = open(alertFile, 'w')
    #    f.close()

    tempFlag = 0
    if tempNum > 80:
        tempFlag = 1
    humFlag = 0
    if humidityNum > 75:
        humFlag = 1

    if alertFlag == 0:
        if tempFlag == 1 and humFlag == 1:
            message = {'Temperature_Alert': True, 'Humidity_Alert': True, 'Temperature': tempNum, 'Humidity': humidityNum, 'Light': lightNum, 'Date': currentDate, 'Time': currentTime, 'DateTime': dateTime}
            alertList.append(message)
            alertFlag = 1
        elif tempFlag == 1:
            message = {'Temperature_Alert': True, 'Humidity_Alert': False, 'Temperature': tempNum, 'Humidity': humidityNum, 'Light': lightNum, 'Date': currentDate, 'Time': currentTime, 'DateTime': dateTime}
            alertList.append(message)
            alertFlag = 1
        elif humFlag == 1:
            message = {'Temperature_Alert': False, 'Humidity_Alert': True, 'Temperature': tempNum, 'Humidity': humidityNum, 'Light': lightNum, 'Date': currentDate, 'Time': currentTime, 'DateTime': dateTime}
            alertList.append(message)
            alertFlag = 1
    
    if alertFlag == 1:
        print ('Alert Triggered')
        with open(alertFile, 'w') as af:
            json.dump(alertList, af)
    else:
        print ('No Alert')

    # Append data to CSV
    with open(iotCSVfile, 'a') as dataFile:
        fWriter = csv.writer(dataFile)
        fWriter.writerow([currentDate, currentTime, tempNum, humidityNum, lightNum, dateTime])

    # Two-second intervals
    time.sleep(2)