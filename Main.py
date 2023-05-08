import multiprocessing as mult
import os
import sys
import time

import paho.mqtt.client as mqtt

import MQTT.MQTT_JSON as mqtt_json
import MQTT.MQTT_Main as mqtt_main

from multiprocessing import Queue

import Reserve.Reserve_Main as reserve

Room = [('balcony', 'balcony main'), ('balcony', 'balcony sub'), ('bath Room', 'bathRoom1'), ('bath Room', 'bathRoom2'),
        ('Big Room', 'big Room1'), ('Big Room', 'big Room2'), ('kitchen', 'kitchen sink')
    , ('kitchen', 'kitchen table'), ('living Room', 'living Room sub'), ('living Room', 'living Room1'),
        ('living Room', 'living Room2'), ('living Room', 'living Room3'), ('middle Room', 'middle Room1')
    , ('middle Room', 'middle Room2'), ('small Room', 'small Room')]

queueToMain = Queue()
sys.path.append(os.getcwd())


class ClientClass:

    def __init__(self):
        self.client_main = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '1', None),
                                        name='switch listen service')
        self.client_and = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '2', queueToMain),
                                       name='android lisetn service')
        self.client_loop = mult.Process(target=ClientClass.MQTT_State, args=(ClientClass, 1), name='state loop service')
        self.client_reserve = mult.Process(target=ClientClass.Reserve_Entrance, args=(ClientClass, queueToMain),
                                           name='light reserve service')

        self.client_and.daemon = True
        self.client_main.daemon = True
        self.client_loop.daemon = True
        self.client_reserve.daemon = True

        self.client_and.start()
        self.client_loop.start()
        self.client_main.start()
        self.client_reserve.start()

        self.mqttClass = None

        self.client_and.join()
        self.client_loop.join()
        self.client_main.join()
        self.client_reserve.join()

        while True:
            if not self.client_main.is_alive():
                exit(-1)
            if not self.client_and.is_alive():
                exit(-1)
            if not self.client_loop.is_alive():
                exit(-1)
            time.sleep(1)

    def MQTT_Main(self, mode, etc):
        self.client = mqtt.Client()
        self.mqttClass = mqtt_main.MQTTClass()
        if mode == '1':  # switch part
            self.mqttClass.on_topicSet('MyHome/Light/Sub/Server')
            self.client.on_message = self.mqttClass.on_message_fromSwitch
        elif mode == '2':  # android part
            self.client.user_data_set(etc)
            self.mqttClass.on_topicSet('MyHome/Light/Pub/Server')
            self.client.on_message = self.mqttClass.on_message_fromAndroid

        self.client.on_connect = self.mqttClass.on_connect

        self.client.connect_async("192.168.0.254", 1883)
        self.client.loop_start()
        while True:
            print(str(mode) +' : '+ str(self.client.is_connected()))
            time.sleep(5)

    def MQTT_State(self, mode):
        self.client_state = mqtt.Client()
        self.client_state.connect_async("192.168.0.254", 1883)
        while True:
            self.client_state.loop()
            # print("MQTT State is run")
            for (cate, room) in Room:
                dic = [('name', 'Server'), ('message', 'STATE'), ('destination', room)]
                object = mqtt_json.JSON_ENCODE_android(dic)
                # print(object)
                self.client_state.publish("MyHome/Light/Pub/" + cate, object)
                time.sleep(4)
            # time.sleep(30)
            self.client_state.loop_stop()
            if mode == 0:
                break

    def Reserve_Entrance(self, queue):
        reserve.ReserveMain(queue)


if __name__ == "__main__":
    mainClass = ClientClass()

