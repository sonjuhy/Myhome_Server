import time
import datetime

import paho.mqtt.client as mqtt
import schedule

import MQTT.MQTT_JSON as mqtt_json

from Network import SQL_Def

Run_able = 0
DoW = ['월', '화', '수', '목', '금', '토', '일']


def ReserveMain(queueToMain):
    print('ReserveMain')
    while True:
        ReserveAdd()
        while True:
            if not queueToMain.empty():
                if queueToMain.get() == "restart":
                    print("In Reserve")
                    break
            schedule.run_pending()
            print(len(schedule.jobs))
            for i in range(0, len(schedule.jobs)):
                print(schedule.jobs[i].tag())
            time.sleep(1)


def ReserveAdd():
    info = ReserveSQL("ReserveSelect")
    run_recode = 0
    for i in range(0, len(info)):
        if info[i][5] == 'False':
            if info[i][6] == 'False':
                run_recode = JobDef(info[i], run_recode)
            else:
                days = info[i][4]
                day = days.split(",")
                n = time.localtime().tm_wday
                for j in range(0, len(day)):
                    if DoW[n] == day[j]:
                        run_recode = JobDef(info[i], run_recode)
    for i in range(0, len(schedule.jobs)):
        print(schedule.jobs[i].at_time)


def ReserveMQTT(action, room, repeat, num):
    print("MQTT Reserve")
    result_list = ReserveSQL("LightList")
    for i in range(0, len(result_list)):
        if room == result_list[i][0]:
            cate = result_list[i][3]
            break
    dic_object = [('name', 'Server'), ('message', action), ('destination', room), ('room', cate)]
    object = mqtt_json.JSON_ENCODE_android(dic_object)

    client = mqtt.Client()
    client.connect("192.168.0.254", 1883)
    client.loop()
    #client.publish("MyHome/Light/Pub/" + room, object)
    client.loop_stop()

    print(dic_object)
    num = str(num)
    diction = [('message', action), ('room', num)]
    SQL_Def("ReserveUpdate", diction)
    print(repeat)
    if repeat == 'False':
        diction = [('activated', "True"), ('room', num)]
        SQL_Def("ReserveUpdateActivated", diction)
        #schedule.clear(num)
        ReserveAdd()


def ReserveSQL(mode):
    result_str = SQL_Def(mode, None)
    list_tmp = []
    for i in result_str:
        tmp = i
        count = (int(len(i) / 9))
        list_tmp.insert(count, tmp)
    return list_tmp


def JobDef(info, first):
    if first == 0:
        JobClear()
    JobAdd(info[1], info[3], info[2], info[6], info[8])  # time, action, room, repeat, num
    return 1


def JobAdd(time, action, room, repeat, num):
    time_list = time.split(':')
    time_hour = int(time_list[0])
    time_min = int(time_list[1])
    timeinfo = datetime.time(time_hour, time_min)
    schedule.every().day.at(str(timeinfo)).do(ReserveMQTT, action, room, repeat, num).tag(num)


def JobClear():
    schedule.clear()
