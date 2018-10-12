from kafka import KafkaProducer
import requests, json, time

osaIP = '129.146.151.215'
kafkaPort = '9092'
address = osaIP + ':' + kafkaPort
iottopic = 'iotcloudforce'
nfctopic = 'nfccloudforce'

iotNextAPI = r'http://localhost:5000/iotnext'
nfcNextAPI = r'http://localhost:5000/nfcnext'
#bcAPI = r'http://localhost:5000/blockchain'

producer = KafkaProducer(bootstrap_servers=[address], api_version=(0,10))

while True:

    # Send any new values to IoT topic
    data = requests.get(iotNextAPI)
    iotvalue = data.json()

    if iotvalue != 'UpToDate':
        print ('SEND IOT: ' + str(data.json()))
        producer.send(iottopic, json.dumps(iotvalue).encode('utf-8'))
    else:
        print ('IOT UP TO DATE')


    # Send any new values to NFC topic
    data = requests.get(nfcNextAPI)
    nfcvalue = data.json()

    if nfcvalue != 'UpToDate':
        print ('SEND NFC: ' + str(data.json()) + '\n')
        producer.send(nfctopic, json.dumps(nfcvalue).encode('utf-8'))
    else:
        print ('NFC UP TO DATE' + '\n')
    


    time.sleep(2)
