import os
import time
import speech_recognition as sr
from gtts import gTTS
import playsound
import pymysql as mysql

import paho.mqtt.client as mqtt
import json


def listen(recognizer, audio):
    now = time.localtime()
    time_str = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday) + ' ' + str(now.tm_hour) + ':' + str(
        now.tm_min)
    print("Sound in Mic")
    try:

        transcript = recognizer.recognize_google(audio, language="ko-KR")
        print("Google Speech Recognition thinks you said " + transcript + " ,time : " + time_str)
        origin_transcript = transcript
        transcript = transcript.replace(" ", "")
        if '시리' in transcript:
            point = transcript.find('시리') + 1
            if '시리야' in transcript or '시리아' in transcript:
                point += 1
            transcript = transcript[point+1:]
            print(transcript)
            answer(transcript, origin_transcript)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def answer(text, origin_voice):
    global audio_text
    room_list = {'큰 베란다': 'balcony main', '작은 베란다': 'balcony sub', '작은 화장실': 'bathRoom2', '큰 화장실': 'bathRoom1',
                 '안방 두번째 스위치': 'big Room2', '안방 첫번째 스위치': 'big Room1', '부엌 탁자': 'kitchen table', '부엌 싱크대': 'kitchen sink',
                 '거실장': 'living Room sub', '거실 세번째 스위치': 'living Room3', '거실 두번째 스위치': 'living Room2',
                 '거실 첫번째 스위치': 'living Room1',
                 '중간방 두번째 스위치': 'middle Room2', '중간방 첫번째 스위치': 'middle Room1', '작은방': 'small room'}

    reverse_room_list = {'balcony main': '큰 베란다', 'balcony sub': '작은 베란다', 'bathRoom1': '큰 화장실', 'bathRoom2': '작은 화장실',
                         'big Room1': '안방 첫번째 스위치', 'big Room2': '안방 두번째 스위치', 'kitchen sink': '부엌 싱크대',
                         'kitchen table': '부엌 탁자',
                         'living Room sub': '거실장', 'living Room1': '거실 첫번째 스위치', 'living Room2': '거실 두번째 스위치',
                         'living Room3': '거실 세번째 스위치',
                         'middle Room1': '중간방 첫번째 스위치', 'middle Room2': '중간방 두번째 스위치', 'small room': '작은방'}

    # category_list = ['balcony', 'bathRoom', 'Big Room', 'living Room', 'middle Room', 'small Room', 'kitchen']

    room_category = {'balcony main': 'balcony', 'balcony sub': 'balcony', 'bathRoom2': 'bathRoom',
                     'bathRoom1': 'bathRoom',
                     'big Room2': 'Big Room', 'big Room1': 'Big Room', 'kitchen sink': 'kitchen',
                     'kitchen table': 'kitchen',
                     'living Room sub': 'living Room', 'living Room3': 'living Room', 'living Room2': 'living Room',
                     'living Room1': 'living Room',
                     'middle Room2': 'middle Room', 'middle Room1': 'middle Room', 'small room': 'small Room'}

    control_room = ''
    category = ''

    if '켜줘' in text:
        point = text.find('켜')
        text = text[:point]
        action = 'ON'
    elif '꺼줘' in text:
        point = text.find('꺼')
        text = text[:point]
        action = 'OFF'
    else:
        speak('원하는 행동을 못들었습니다. 다시 한번 말씀해주세요')
        now = time.localtime()
        time_str = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday) + ' ' + str(
            now.tm_hour) + ':' + str(now.tm_min)
        data = (control_room, origin_voice, control_room + ' no_action', time_str, 'false')
        sql('record', control_room, data)
        return

    for room in room_list:
        compare_category = room_category[room_list[room]]
        if compare_category == 'balcony':
            compare_room = room.split(" ")[1]
        elif compare_category == 'Big Room' or compare_category == 'living Room' or compare_category == 'middle Room' or compare_category == 'kitchen':
            compare_room = room.split(" ")[0]
        else:
            compare_room = room.replace(" ", "")

        if compare_room in text:
            control_room = room_list[room]
            category = room_category[control_room]

    if category == '':
        if not control_room == '':
            count = 0
            duplication_list = {}
            tmp_category = room_category[control_room]
            for key, value in room_category.items():
                if value == tmp_category:
                    duplication_list[count] = reverse_room_list[key]
                    count += 1
                    if count > 1:
                        break
            if count == 1:
                category = room_category[control_room]
            else:
                info_text = '해당 카테고리에 속한 전등은 '
                for num in duplication_list:
                    info_text += duplication_list[num] + ", "
                info_text += '입니다. 다시 말씀해 주세요.'
                speak(info_text)
                now = time.localtime()
                time_str = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday) + ' ' + str(
                    now.tm_hour) + ':' + str(now.tm_min)
                data = (control_room, origin_voice, control_room + ' ' + action, time_str, 'false')
                sql('record', control_room, data)
                return
    else:
        if '불' in text:
            if category == 'living Room' or category == 'middle Room' or category == 'Big Room':
                if '스위치' in text:
                    text = text.replace('불', '')
                else:
                    text = text.replace('불', '스위치')
            else:
                if '스위치' not in text:
                    text = text.replace('불', '')
                else:
                    text = text.replace('불', '스위치')

        for room in room_list:
            tmp_text = text
            if tmp_text == room or tmp_text == room.replace(" ", ""):
                control_room = room_list[room]
                category = room_category[room_list[room]]

    if category == '':
        speak('전등을 찾지 못했습니다. 다시 말씀해주세요')
        now = time.localtime()
        time_str = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday) + ' ' + str(
            now.tm_hour) + ':' + str(now.tm_min)
        data = (control_room, origin_voice, 'no_room ' + action, time_str, 'false')
        sql('record', control_room, data)
    else:
        result_sql = sql('state', control_room, '')
        state = True
        if result_sql[1] == 'On':
            compare_state = 'ON'
            if compare_state == action:
                state = False
                audio_text = reverse_room_list[control_room] + ' 불은 이미 켜져 있습니다.'
        else:
            compare_state = 'OFF'
            if compare_state == action:
                state = False
                audio_text = reverse_room_list[control_room] + ' 불은 이미 꺼져 있습니다.'

        if state:
            mqtt_def(category, control_room, action)
            now = time.localtime()
            time_str = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday) + ' ' + str(now.tm_hour) + ':' + str(now.tm_min)
            data = (control_room, origin_voice, control_room + ' : ' + action, time_str, 'true')
            sql('record', control_room, data)
            if action == 'ON':
                action_speak = '켰습니다'
            else:
                action_speak = '껐습니다'

            audio_text = reverse_room_list[control_room] + ' 불을 ' + action_speak

        speak(audio_text)


def sql(mode, light, action):
    user = 'sonjuhy_home'
    password = 'son278298@'
    host = '192.168.0.254'
    db = 'Home'
    port = 3306
    conn = mysql.connect(host=host, port=port, user=user, passwd=password, db=db, charset='utf8')
    if conn.open:
        curs = conn.cursor()
        if mode == 'record':
            sql_str = 'INSERT INTO Voice_Record (Room, voice, action, time, result) VALUES (%s, %s, %s, %s, %s)'
            if len(action[1]) >= 500:
                action_str = action[1]
                action = (action[0], 'error '+action_str[:490], action[2], action[3], action[4])
            if len(action[4]) >= 500:
                action_str = action[4]
                action = (action[0], action[1], action[2], action[3], 'error '+action_str[:499])
            curs.execute(sql_str, action)
            conn.commit()
        elif mode == 'state':
            sql_str = 'SELECT * FROM Room_Light WHERE Room = "'+light+'"'
            curs.execute(sql_str)
            res = curs.fetchone()
            conn.commit()
            return res


def mqtt_def(category, room, action):
    sender = "ai"
    json_str = {"Light": {"sender": sender, "message": action, "room": category, "destination": room}}
    json_object = json.dumps(json_str)
    print(json_object)

    mqtt_client = mqtt.Client()
    mqtt_client.connect("192.168.0.254", 1883)
    mqtt_client.loop()

    if not mqtt_client.is_connected():
        mqtt_client.connect("192.168.0.254", 1883)

    mqtt_client.publish('MyHome/Light/Pub/Server', json_object)

    mqtt_client.loop_stop()


def speak(text):
    print('saying', end='...')
    tts = gTTS(text=text, lang='ko')
    filename = 'audio.mp3'
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)
    print(' [speak] : ' + text)


r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)

speak('말씀하세요.')
stop_listening = r.listen_in_background(m, listen, phrase_time_limit=4)

while True:
    time.sleep(0.1)
