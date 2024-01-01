import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print(f'Recieved message: {str(message.payload.decode("utf-8"))}')


TOPIC = 'orinlakantobad'
mqtt_broker = 'broker.hivemq.com'
# mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client('Smartphone')
client.connect(mqtt_broker)

client.on_message = on_message
client.subscribe(TOPIC)

# client.loop_start()
# client.loop_forever()

# client.subscribe('TEMPERATURE')


# time.sleep(30)

client.loop_forever()

# client.disconnect()
# client.loop_forever(retry_first_connection=True)
