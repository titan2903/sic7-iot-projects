# filepath:
# TLS-enabled MQTT subscribe test for HiveMQ Cloud
import ssl
import time
from paho.mqtt.client import Client, MQTTv311

BROKER = "ab36ea92cee24b64acda14d3001e34d4.s1.eu.hivemq.cloud"
PORT = 8883
USER = "cakrawala_mqtt"
PASSWORD = "vXtbU7m2DjTxBSLN"
TOPIC = "home/config/test"


def on_connect(client, userdata, flags, rc):
    print("on_connect rc:", rc)
    if rc == 0:
        print("Connected OK — subscribing to", TOPIC)
        client.subscribe(TOPIC, qos=0)
    else:
        print("Connect failed, rc=", rc)


def on_subscribe(client, userdata, mid, granted_qos):
    print("on_subscribe mid:", mid, "granted_qos:", granted_qos)
    if len(granted_qos) and granted_qos[0] == 128:
        print(
            "SUBSCRIBE was refused by broker (granted_qos=128) -> check ACL/permissions"
        )


def on_message(client, userdata, msg):
    print("MSG:", msg.topic, msg.payload)


def on_log(client, userdata, level, buf):
    print("LOG:", buf)


c = Client(client_id="test-client-siragas", protocol=MQTTv311)
c.username_pw_set(USER, PASSWORD)
c.on_connect = on_connect
c.on_subscribe = on_subscribe
c.on_message = on_message
c.on_log = on_log

# Create an SSL context using system CA certs
ctx = ssl.create_default_context()
# If you want to skip cert validation for quick testing ONLY:
# ctx.check_hostname = False
# ctx.verify_mode = ssl.CERT_NONE

c.tls_set_context(ctx)

try:
    c.connect(BROKER, PORT, 60)
    c.loop_start()
    # keep running to observe callbacks
    time.sleep(10)
finally:
    c.loop_stop()
    c.disconnect()
