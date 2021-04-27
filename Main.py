import datetime
import os
import sys
import time
import schedule
import multiprocessing as mult
import paho.mqtt.client as mqtt
import MQTT.MQTT_Main as mqtt_main
import MQTT.MQTT_JSON as mqtt_json

Room = [('balcony', 'balcony main'), ('balcony', 'balcony sub'), ('bath Room', 'bathRoom1'), ('bath Room', 'bathRoom2'),
        ('Big Room', 'big Room1'), ('Big Room', 'big Room2'), ('kitchen', 'kitchen sink')
    , ('kitchen', 'kitchen table'), ('living Room', 'living Room sub'), ('living Room', 'living Room1'),
        ('living Room', 'living Room2'), ('living Room', 'living Room3'), ('middle Room', 'middle Room1')
    , ('middle Room', 'middle Room2'), ('small Room', 'small Room')]


class MQTT_Class:

    def __init__(self):
        self.client_main = mult.Process(target=MQTT_Class.MQTT_Main, args=(MQTT_Class, '1'), name='default service')
        self.client_and = mult.Process(target=MQTT_Class.MQTT_Main, args=(MQTT_Class, '2'), name='android service')
        self.client_state = mult.Process(target=MQTT_Class.MQTT_Main, args=(MQTT_Class, '3'), name='state check service')
        self.client_loop = mult.Process(target=MQTT_Class.MQTT_State, args=(MQTT_Class, 1), name='state loop service')
        #self.client_check = Process(target=MQTT_Class.MQTT_Client_Restart, args=(self, 1), name="restart service")
        print("start")
        print(sys.version)

        self.client_main.daemon = True
        self.client_and.daemon = True
        self.client_state.daemon = True
        self.client_loop.daemon = True

        self.client_main.start()
        self.client_and.start()
        self.client_state.start()
        self.client_loop.start()
        #self.client_check.start()

        while True:
            if self.client_main.is_alive():
                print('client is alive')
            else:
                self.client_main.run()
                print('client is run')
            if self.client_and.is_alive():
                print('client_and is alive')
            else:
                self.client_and.close()
                self.client_and.run()
                print('client_and is run')
            time.sleep(4)

        self.client_main.join()
        self.client_and.join()
        self.client_state.join()
        self.client_loop.join()
        #self.client_check.join()

    # def MQTT_Client_Manage(self):

    def MQTT_Main(self, mode):
        self.client = mqtt.Client()
        if mode == "1":
            self.client.on_connect = mqtt_main.on_connect
            self.client.on_message = mqtt_main.on_message
        else:
            if mode == "2":
                self.client.on_connect = mqtt_main.on_connect_android
                self.client.on_message = mqtt_main.on_message_android
            else:
                self.client.on_connect = mqtt_main.on_connect_state
                self.client.on_message = mqtt_main.on_message

        self.client.connect("192.168.0.254", 1883)
        self.client.loop_forever()

    def MQTT_State(self, mode):
        self.client_state = mqtt.Client()
        self.client_state.connect("192.168.0.254", 1883)
        while True:
            self.client_state.loop()
            for (cate, room) in Room:
                dic = [('name', 'Server'), ('message', 'STATE'), ('destination', room)]
                object = mqtt_json.JSON_ENCODE_android(dic)
                print(object)
                self.client_state.publish("MyHome/Light/Pub/" + cate, object)
                time.sleep(4)
            # time.sleep(30)
            self.client_state.loop_stop()
            if mode == 0:
                break;





if __name__ == "__main__":
    #mainClass = MQTT_Class()
    dt = datetime.datetime.today().weekday()
    print(dt)

