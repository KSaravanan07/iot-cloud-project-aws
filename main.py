from awsiot import mqtt_connection_builder
from awsiot import mqtt
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import json


# MQTT endpoint for your AWS region
my_endpoint = "your-iot-thing-endpoint"

# Thing name
client_id = "your-unique-id-for-this-connection"
root_ca_path = "your-root-certificate-downloaded-from-aws-iot-core-file-path"   # Root CA file path
certificate_path = "your-thing-certificate-downloaded-from-aws-iot-core-file-path"  # Thing certificate file path
private_key_path = "your-thing-private-key-downloaded-from-aws-iot-core-file-path"  # Thing private key file path

# Topic to publish to
topic = "temperature"
subscribe_topic = "prediction"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUZZER_PIN_BCM = 27
DHT_PIN_BCM = 17
DHT_SENSOR = Adafruit_DHT.DHT11

GPIO.setup(BUZZER_PIN_BCM, GPIO.OUT)
GPIO.output(BUZZER_PIN_BCM, GPIO.LOW)

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=my_endpoint,
    cert_filepath=certificate_path,
    pri_key_filepath=private_key_path,
    client_bootstrap=None,
    ca_filepath=root_ca_path,
    client_id=client_id,
    clean_session=False,
    keep_alive_secs=60,
    http_proxy_options=None)

# Create an MQTT client
connect_future = mqtt_connection.connect()
connection = connect_future.result()
print(connection)

if connection['session_present']:
    subscription = mqtt_connection.subscribe(topic=subscribe_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=lambda topic, payload: print(f"Received message from topic {topic}: {payload}"))
    mqtt_connection.on_message = lambda topic, payload: print(f"Received message from topic {topic}: {payload}")

# Dummy Data to publish
# message = {"temperature": 21, "humidity": 60}


try:
    while True:
        temperature, humidity = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN_BCM)
        
        if temperature is not None and humidity is not None:
            payload = {"temperature": temperature, 'humidity': humidity}
            mqtt_connection.publish(topic=topic, payload=json.dumps(payload), qos=mqtt.QoS.AT_LEAST_ONCE)
            print(f"Published temperature: {temperature} Â°C, humidity: {humidity} %")
        else:
            print("Failed to retrieve temperature data")
        time.sleep(15)
        
except KeyboardInterrupt:
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    result = disconnect_future.result()
    print(result)
