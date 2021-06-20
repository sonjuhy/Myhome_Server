import multiprocessing as mult
import sys
import time

import paho.mqtt.client as mqtt

import MQTT.MQTT_JSON as mqtt_json
import MQTT.MQTT_Main as mqtt_main

from multiprocessing import Queue

import requests as request

import Reserve.Reserve_Main as reserve

Room = [('balcony', 'balcony main'), ('balcony', 'balcony sub'), ('bath Room', 'bathRoom1'), ('bath Room', 'bathRoom2'),
        ('Big Room', 'big Room1'), ('Big Room', 'big Room2'), ('kitchen', 'kitchen sink')
    , ('kitchen', 'kitchen table'), ('living Room', 'living Room sub'), ('living Room', 'living Room1'),
        ('living Room', 'living Room2'), ('living Room', 'living Room3'), ('middle Room', 'middle Room1')
    , ('middle Room', 'middle Room2'), ('small Room', 'small Room')]

queueToMain = Queue()

class ClientClass:

    def __init__(self):
        self.client_main = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '1', None), name='switch listen service')
        self.client_and = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '2', queueToMain), name='android lisetn service')
        self.client_reserve = mult.Process(target=ClientClass.Reserve_Entrance, args=(ClientClass, queueToMain),
                                           name='light reserve service')
        self.client_loop = mult.Process(target=ClientClass.MQTT_State, args=(ClientClass, 1), name='state loop service')

        '''self.client_main = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '1', None), name='default service')
        self.client_and = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '2', None), name='android service')
        self.client_state = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, '3', None), name='state check service')
        self.client_loop = mult.Process(target=ClientClass.MQTT_State, args=(ClientClass, 1), name='state loop service')
        self.client_reserve = mult.Process(target=ClientClass.Reserve_Entrance, args=(ClientClass, queueToMain), name='light reserve service')
        self.client_reserve_mqtt = mult.Process(target=ClientClass.MQTT_Main, args=(ClientClass, 4, queueToMain), name='reserve mqtt service')'''

        print("start")
        print(sys.version)

        #self.client_main.daemon = True
        self.client_and.daemon = True
        #self.client_state.daemon = True
        self.client_loop.daemon = True
        #self.client_reserve.daemon = True
        #self.client_reserve_mqtt.daemon = True

        #self.client_main.start()
        self.client_and.start()
        #self.client_state.start()
        #self.client_loop.start()
        self.client_reserve.start()
        #self.client_reserve_mqtt.start()

        self.mqttClass = None

        self.client_main.join()
        self.client_and.join()
        self.client_state.join()
        self.client_loop.join()
        self.client_reserve.join()
        self.client_reserve_mqtt.join()

        while True:
            if not self.client_main.is_alive():
                exit(-1)
            if not self.client_and.is_alive():
                exit(-1)
            if not self.client_loop.is_alive():
                exit(-1)
            '''if not self.client_state.is_alive():
                if not self.client_reserve.is_alive():
                    exit()
                exit()
            if not self.client_reserve_mqtt.is_alive():
                exit()'''
            time.sleep(1)

    def MQTT_Main(self, mode, etc):
        self.client = mqtt.Client()
        self.mqttClass = mqtt_main.MQTTClass()
        if mode == '1':  # switch part
            self.mqttClass.on_topicSet('MyHome/Light/Sub/Server')
            self.client.on_message = self.mqttClass.on_message_fromSwitch
        else:
            if mode == '2':  # android part
                self.client.user_data_set(etc)
                self.mqttClass.on_topicSet('MyHome/Light/Pub/Server')
                self.client.on_message = self.mqttClass.on_message_fromAndroid

        self.client.on_connect = self.mqttClass.on_connect

        '''if mode == "1":  # All data listen from switch            
            self.client.on_connect = mqtt_main.on_connect
            self.client.on_message = mqtt_main.on_message
        else:
            if mode == "2":  # All data listen from android
                self.client.on_connect = mqtt_main.on_connect_android
                self.client.on_message = mqtt_main.on_message_android
            else:
                if mode == "3":  # State data listen from switch
                    self.client.on_connect = mqtt_main.on_connect_state
                    self.client.on_message = mqtt_main.on_message
                else:  # Reserve data listen from android
                    self.client.user_data_set(etc)
                    self.client.on_connect = mqtt_main.on_connect_reserve
                    self.client.on_message = mqtt_main.on_message_reserve'''

        self.client.connect("192.168.0.254", 1883)
        self.client.loop_forever()

    def MQTT_State(self, mode):
        self.client_state = mqtt.Client()
        self.client_state.connect("192.168.0.254", 1883)
        while True:
            self.client_state.loop()
            #print("MQTT State is run")
            for (cate, room) in Room:
                dic = [('name', 'Server'), ('message', 'STATE'), ('destination', room)]
                object = mqtt_json.JSON_ENCODE_android(dic)
                #print(object)
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
    '''url = "http://sonjuhy.iptime.org/testphp.php"
    datas = {'data': 'test room'}
    header = {'Content-Type': 'application/json; charset=utf-8'}
    response = request.post(url=url, data=datas)
    print(response.text)
    print(response.status_code)'''





