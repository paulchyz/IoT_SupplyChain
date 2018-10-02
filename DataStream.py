import requests, time, csv, os.path

# Make CSV and add headers if file does not exist
if not os.path.isfile(r'/Users/pchyz/Documents/AppDev/Capstone/data.csv'):
    f = open('data.csv', 'w')
    fWriter = csv.writer(f)
    fWriter.writerow(['yr/mo/d','time','temperature','humidity','light'])
    f.close()

# Infinite loop
while True:

    # Get humidity
    humidity = requests.get(r'https://us.wio.seeed.io/v1/node/GroveTempHumD1/humidity?access_token=8404488f6918fedac5c894255cf58d88')
    humidityNum = humidity.json()['humidity']
    print('Humidity: ' + str(humidityNum))

    # Get light
    light = requests.get(r'https://us.wio.seeed.io/v1/node/GroveDigitalLightI2C0/lux?access_token=8404488f6918fedac5c894255cf58d88')
    lightNum = light.json()['lux']
    print('Light: ' + str(lightNum))

    # Get temp
    temp = requests.get(r'https://us.wio.seeed.io/v1/node/GroveTempHumD1/temperature_f?access_token=8404488f6918fedac5c894255cf58d88')
    tempNum = temp.json()['fahrenheit_degree']
    print('Temp: ' + str(tempNum))

    # Get date and time
    currentDate = time.strftime('%Y/%m/%d', time.gmtime())
    currentTime = time.strftime('%H:%M:%S', time.gmtime())

    # Append data to CSV
    with open('data.csv', 'a') as dataFile:
        fWriter = csv.writer(dataFile)
        fWriter.writerow([currentDate, currentTime, tempNum, humidityNum, lightNum])
    
    # Two-second intervals
    time.sleep(2)