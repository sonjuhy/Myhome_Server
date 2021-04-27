import json


def JSON_Parser(object):
    print(object)
    jsonObject = json.loads(object)
    dic = {'sender': jsonObject['sender'], 'message': jsonObject['message'], 'room': jsonObject['room']}
    return dic


def JSON_Parser_android(object):
    jsonObject = json.loads(object)
    dic = {'sender': jsonObject['Light']['sender'], 'message': jsonObject['Light']['message'],
           'room': jsonObject['Light']['room'], 'destination': jsonObject['Light']['destination']}
    return dic


def JSON_ENCODE(dic):
    object = {"sender": dic['sender'], "message": dic['message'], "room": dic['room']}
    jsonObject = json.dumps(object)
    return jsonObject


def JSON_ENCODE_android(dic):
    object = {"Light": {"sender": dic[0][1], "message": dic[1][1], "destination": dic[2][1]}}
    jsonObject = json.dumps(object)
    return jsonObject