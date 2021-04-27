import time

import paho.mqtt.client as mqtt
import pymysql
import Network as network
import MQTT.MQTT_JSON as json

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


def SQL_def():
    conn = pymysql.connect(host=Host, port=Port, user=User, password=Password, db=DB, charset='utf8')
    if conn.open:
        with conn.cursor() as curs:
            # SQL_Update('a', Mode_O)
            print("sql def")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Sub/Server")
    print("Connected with result code(Sub) : "+str(rc))


def on_connect_android(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Pub/Server")
    print("Connected with result code(and) : " + str(rc))


def on_connect_state(client, userdata, flags, rc):
    client.subscribe("MyHome/Light/Sub/Server/State")
    #client.subscribe("/MyHome/Light/Pub/test/living Room")
    print("Connected with result code(State) : " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    payload = msg.payload.decode("utf-8")

    if payload is None:
        None
    else:
        if payload is not None and payload[0] == "{" and payload[-1] == "}":
            dic = json.JSON_Parser(payload)
            if dic['sender'] == 'Server':
                if dic['room'] in Room:
                    Room[dic['room']] = "On"
                    network.SQL_Def("Light", dic)
                    print("room : "+dic['room'])
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
        None
    else:
        if payload is not None and payload[0] == "{" and payload[-1] == "}":
            dic = json.JSON_Parser_android(payload)
            print(dic)
            on_publish_switch(payload, dic['room'])


def on_publish(payload):
    mqttp = mqtt.Client()
    mqttp.connect("192.168.0.254", 1883)
    mqttp.publish("MyHome/Light/Result", payload)
    mqttp.loop(3)


def on_publish_switch(payload, room):
    mqttp = mqtt.Client()
    mqttp.connect("192.168.0.254", 1883)
    mqttp.publish("MyHome/Light/Pub/"+room, payload)
    mqttp.loop(3)


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.0.254", 1883)
    client.loop_forever()