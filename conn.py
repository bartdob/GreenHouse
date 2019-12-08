#  /usr/bin/python
#  -*- coding: utf-8 -*-

def ConnectDB():
    
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='szklarnia',
                                             user='root',
                                             password='honey666')

        if connection.is_connected():
            print("Connected to MySQL Server szklarnia")


    except Error as e:
        print("Error while connecting to MySQL", e)
        
    return connection

def CloseDB(db):
    db.close