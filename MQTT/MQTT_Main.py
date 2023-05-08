import paho.mqtt.client as mqtt
import Network as network
import MQTT.MQTT_JSON as json


class MQTTClass:
    User = 'sonjuhy_home'
    Password = "son278298@"
    Host = "192.168.0.254"
    DB = "Home"
    Port = 3306
    Mode_O = "'OFF'"

    Room = {'balcony main': 'Off', 'balcony sub': 'Off', 'bathRoom1': 'Off', 'bathRoom2': 'Off',
            'big Room1': 'Off', 'big Room2': 'Off', 'kitchen sink': 'Off'
        , 'kitchen table': 'Off', 'living Room sub': 'Off', 'living Room1': 'Off',
            'living Room2': 'Off', 'living Room3': 'Off', 'middle Room1': 'Off'
        , 'middle Room2': 'Off', 'small Room': 'Off'}

    def __init__(self):
        self.topic = None
        self.payload = None
        self.dict = []
        self.diction = []
        self.queue = None
        self.mqttClient = mqtt.Client()
        self.mqttClient.connect_async("192.168.0.254", 1883)
        self.mqttclient_pub = mqtt.Client()
        self.mqttclient_pub.connect_async("192.168.0.254", 1883)

    def on_topicSet(self, topic):
        self.topic = topic
        print(self.topic)

    def on_connect(self, client, user_data, flags, rc):
        client.subscribe(topic=str(self.topic))
        print("Connected with result code(Sub) : " + str(rc))

    def on_message_fromAndroid(self, client, user_data, msg):
        self.payload = msg.payload.decode("utf-8")
        print("from Android message")
        print(self.payload)
        if self.payload is not None:
            if self.payload == 'reserve':
                print("from android if")
                if user_data is not None:
                    self.queue = user_data
                    self.queue.put("restart")
            else:
                print("from android else")
                self.dict = json.JSON_Parser_android(self.payload)
                self.on_publish('MyHome/Light/Pub/'+self.dict['room'], self.payload)

    def on_message_fromSwitch(self, client, user_data, msg):
        self.payload = msg.payload.decode("utf-8")
        #print("from switch : " + self.payload)
        if self.payload is not None and self.payload[0] == "{" and self.payload[-1] == "}":
            self.dict = json.JSON_Parser(self.payload)
            if self.dict['sender'] == 'Server':  # return control data part
                if self.dict['room'] in self.Room:
                    self.Room[self.dict['room']] = "On"
                    network.SQL_Def("Light", self.dict)
                    if self.dict['room'] == 'small Room':
                        for (room, state) in self.Room.items():
                            self.diction = [('message', state), ('room', room)]
                            network.SQL_Def("Connect", self.diction)
                            self.Room[room] = "Off"
            else:  # Light state part
                network.SQL_Def("LightRecord", self.dict)
                network.SQL_Def("Light", self.dict)
                self.diction = json.JSON_ENCODE(self.dict)
                self.on_publish('MyHome/Light/Result', self.diction)
        else:
            print("can't work in on_message")
            print(self.payload)

    def on_publish(self, topic, payload):
        print("on_publish")
        print(topic)
        print(payload)
        if not self.mqttclient_pub.is_connected():
            self.mqttclient_pub.connect("192.168.0.254", 1883)
            print("mqtt reconnected")
        self.mqttclient_pub.loop()
        result = self.mqttclient_pub.publish(topic, payload)
        self.mqttclient_pub.loop_stop()
        print(result)
        self.mqttclient_pub.disconnect()
