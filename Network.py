# import MySQLdb
import pymysql as MySQLdb
import requests
import time

User = 'DB ID'
Password = "DB Password"
Host = "192.168.0.254"
DB = "table name"
Port = 3306
Mode_O = "'OFF'"


def SQL_Def(mode, dic):
    conn = MySQLdb.connect(host=Host, port=Port, user=User, passwd=Password, db=DB, charset='utf8')
    if conn.open:
        curs = conn.cursor()
        # print(mode)
        if mode == "Light":
            if dic['message'] == "On" or dic['message'] == "Off":
                SQL_Update(dic['message'], dic['room'], curs, conn, "Room_Light", "State", 'room')
        elif mode == "LightList":
            result = SQL_Select("Room_Light", curs, conn)
            return result
        elif mode == "LightRecord":
            now = time.localtime()
            date = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday)
            hour = str(now.tm_hour) + ':' + str(now.tm_min)
            data = (hour, dic['room'], dic['message'], date, dic['sender'])
            SQL_Insert("LightRecord", curs, conn, data)
        elif mode == "Connect":
            SQL_Update(dic[0][1], dic[1][1], curs, conn, "Room_Light", "Connect", 'room')
        elif mode == "ReserveSelect":
            result = SQL_Select("Light_Reserve", curs, conn)
            return result
        elif mode == "ReserveUpdate":
            SQL_Update(dic[0][1], dic[1][1], curs, conn, "Light_Reserve", "Do", "num")
        elif mode == "ReserveUpdateActivated":
            SQL_Update(dic[0][1], dic[1][1], curs, conn, "Light_Reserve", "Activated", "num")
            # state = SQL_State(curs)


def SQL_Insert(table, cur, connect, data):
    sql = 'INSERT INTO ' + table + ' ( Time, Room, Do, Day, User ) VALUES (%s, %s, %s, %s, %s)'
    res = cur.execute(sql, data)
    connect.commit()


def SQL_Update(state, condition, cur, connect, table, column, mode):
    if mode == 'room':
        sql = 'UPDATE ' + table + ' SET ' + column + ' = "' + state + '" WHERE Room = "' + condition + '"'
    else:
        if mode == 'num':
            sql = 'UPDATE ' + table + ' SET ' + column + ' = "' + state + '" WHERE Num = "' + condition + '"'
    # print(sql)
    res = cur.execute(sql)
    connect.commit()
    # print("sql update")
    # print(res)


def SQL_Select(table, cur, connect):
    sql = 'SELECT * FROM ' + table
    # print(sql)
    cur.execute(sql)
    res = cur.fetchall()
    connect.commit()
    return res


