import ssl, time
from paho.mqtt.client import Client, MQTTv311

BROKER = "ab36ea92cee24b64acda14d3001e34d4.s1.eu.hivemq.cloud"
PORT = 8883
USER = "cakrawala_mqtt"
PASSWORD = "vXtbU7m2DjTxBSLN"
TOPIC = "home/config/test"
PAYLOAD = '{"interval_ms":2000}'


def on_connect(client, userdata, flags, rc):
    print("on_connect rc:", rc)


c = Client(client_id="test-client-pub", protocol=MQTTv311)
c.username_pw_set(USER, PASSWORD)
c.on_connect = on_connect

ctx = ssl.create_default_context()
c.tls_set_context(ctx)

c.connect(BROKER, PORT, 60)
c.loop_start()
time.sleep(1)
print("Publishing:", PAYLOAD)
c.publish(TOPIC, PAYLOAD, qos=0, retain=False)
time.sleep(1)
c.loop_stop()
c.disconnect()
