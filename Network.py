import MySQLdb

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
                SQL_Update(dic['message'], dic['room'], curs, conn, "State")
        else:
            if mode == "Connect":
                SQL_Update(dic[0][1], dic[1][1], curs, conn, "Connect")
            else:
                if mode == "Reserve":
                    print("dd")
            # state = SQL_State(curs)


def SQL_Update(state, room, cur, connect, table):
    sql = 'UPDATE Room_Light SET '+table+' = "'+state+'" WHERE Room = "' + room +'"'
    print(sql)
    res = cur.execute(sql)
    connect.commit()
    print("sql update")
    print(res)


def SQL_Select(table, cur, connect):
    sql = 'SELECT * FROM ' + table
    print(sql)
    res = cur.execute(sql)
    connect.commit()
