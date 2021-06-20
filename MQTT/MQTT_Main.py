import paho.mqtt.client as mqtt
import Network as network
import MQTT.MQTT_JSON as json
'''
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


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Sub/Server")
    print("Connected with result code(Sub) : " + str(rc))


def on_connect_android(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Pub/Server")
    print("Connected with result code(and) : " + str(rc))


def on_connect_state(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Sub/Server/State")
    print("Connected with result code(State) : " + str(rc))


def on_connect_reserve(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Reserve/Pub")
    print("Connected with result code(light_reserve) : " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    payload = msg.payload.decode("utf-8")

    if payload is None:
        pass
    else:
        if payload is not None and payload[0] == "{" and payload[-1] == "}":
            dic = json.JSON_Parser(payload)
            if dic['sender'] == 'Server':
                if dic['room'] in Room:
                    Room[dic['room']] = "On"
                    network.SQL_Def("Light", dic)
                    print("room : " + dic['room'])
                    if dic['room'] == 'small Room':
                        print(Room)
                        for (room, state) in Room.items():
                            diction = [('message', state), ('room', room)]
                            network.SQL_Def("Connect", diction)
                            Room[room] = "Off"
            else:
                print("from switch")
                print(payload)
                print(dic)
                network.SQL_Def("Light", dic)
                diction = json.JSON_ENCODE(dic)
                on_publish(diction)
        else:
            print("can't work in on_message")
            print(payload)


def on_message_android(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print("on message android part")
    print(payload)
    if payload is None:
        pass
    else:
        if payload is not None and payload[0] == "{" and payload[-1] == "}":
            dic = json.JSON_Parser_android(payload)
            print(dic)
            on_publish_switch(payload, dic['room'])


def on_message_reserve(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    queue = userdata
    print("on message light_reserve part")
    if payload is None:
        None
    else:
        queue.put("restart")


def on_publish(payload):
    mqttp = mqtt.Client()
    mqttp.connect("192.168.0.254", 1883)
    mqttp.publish("MyHome/Light/Result", payload)
    mqttp.loop(3)


def on_publish_switch(payload, room):
    mqttp = mqtt.Client()
    mqttp.connect("192.168.0.254", 1883)
    mqttp.publish("MyHome/Light/Pub/" + room, payload)
    mqttp.loop(3)'''


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
        self.mqttClient.connect("192.168.0.254", 1883)

    def on_topicSet(self, topic):
        self.topic = topic
        print(self.topic)

    def on_connect(self, client, user_data, flags, rc):
        #print("topic in mqtt class : " + self.topic)
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
        if self.payload is not None and self.payload[0] == "{" and self.payload[-1] == "}":
            self.dict = json.JSON_Parser(self.payload)
            if self.dict['sender'] == 'Server':  # return control data part
                if self.dict['room'] in Room:
                    Room[self.dict['room']] = "On"
                    network.SQL_Def("Light", self.dict)
                    #print("room : " + self.dict['room'])
                    if self.dict['room'] == 'small Room':
                        for (room, state) in Room.items():
                            self.diction = [('message', state), ('room', room)]
                            network.SQL_Def("Connect", self.diction)
                            Room[room] = "Off"
            else:  # Light state part
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
        self.mqttClient.publish(topic, payload)
        self.mqttClient.loop(3)
