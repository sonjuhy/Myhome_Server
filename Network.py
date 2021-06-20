import MySQLdb
import requests

User = 'sonjuhy_home'
Password = "son278298@"
Host = "192.168.0.254"
DB = "Home"
Port = 3306
Mode_O = "'OFF'"


def SQL_Def(mode, dic):
    conn = MySQLdb.connect(host=Host, port=Port, user=User, passwd=Password, db=DB, charset='utf8')
    if conn.open:
        curs = conn.cursor()
        print(mode)
        if mode == "Light":
            if dic['message'] == "On" or dic['message'] == "Off":
                SQL_Update(dic['message'], dic['room'], curs, conn, "Room_Light", "State", 'room')
        else:
            if mode == "LightList":
                result = SQL_Select("Room_Light", curs, conn)
                return result
            else:
                if mode == "Connect":
                    SQL_Update(dic[0][1], dic[1][1], curs, conn, "Room_Light", "Connect", 'room')
                else:
                    if mode == "ReserveSelect":
                        result = SQL_Select("Light_Reserve", curs, conn)
                        return result
                    else:
                        if mode == "ReserveUpdate":
                            SQL_Update(dic[0][1], dic[1][1], curs, conn, "Light_Reserve", "Do", "num")
                        else:
                            if mode == "ReserveUpdateActivated":
                                SQL_Update(dic[0][1], dic[1][1], curs, conn, "Light_Reserve", "Activated", "num")
            # state = SQL_State(curs)


def SQL_Update(state, condition, cur, connect, table, column, mode):
    if mode == 'room':
        sql = 'UPDATE ' + table + ' SET ' + column + ' = "' + state + '" WHERE Room = "' + condition + '"'
    else:
        if mode == 'num':
            sql = 'UPDATE ' + table + ' SET ' + column + ' = "' + state + '" WHERE Num = "' + condition + '"'
    print(sql)
    res = cur.execute(sql)
    connect.commit()
    print("sql update")
    print(res)


def SQL_Select(table, cur, connect):
    sql = 'SELECT * FROM ' + table
    print(sql)
    cur.execute(sql)
    res = cur.fetchall()
    connect.commit()
    return res


def POST_Sender(room, activity, name):
    data = {'Room': room,
            'message': activity,
            'Sender': name}
    link = 'http://sonjuhy.iptime.org/home/PostToSwitch.php'
    response = requests.post(link, data=data)
    if response.status_code == 200:
        print("Working")
    else:
        print("Error to php")
