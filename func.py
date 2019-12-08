#  /usr/bin/python
#  -*- coding: utf-8 -*-


def sensors():	#arduino #python
    MajDBMesures("TPINT",'Temp_int')
    MajDBMesures("LUMIN",'Lumin')
    MajDBMesures("HUMID",'Humidity')
    #ser.close() 

def dataFromArduino():
                    
    sensors()
 
    time.sleep(1)
     # jasność
    
    MajDBEquip("LAMPEET",'Lamp') 
    MajDBEquip("POMPEET",'Pomp')
    MajDBEquip("HEATET", 'Heat')
    MajDBEquip("VENTIET",'Vent')
    

    MajCounter("LAMPECP",'Lamp')
    MajCounter("POMPECP",'Pomp')
    MajCounter("HEATCP", 'Heat')
    MajCounter("VENTICP",'Vent') 

    sensors()

#-------------------------------Funkcja odczytująca stan sprzętu on/off--------------


def MajDBEquip(Commande,Equip): 
    db = ConnectDB()
    curs = db.cursor()
   
    while True:
        try:
            ser.write(Commande)
            time.sleep(1)
            RetCom=(ser.readline().strip().decode("UTF-8"))
            
            curs.execute("UPDATE control SET Stan=%s WHERE Equipement=%s;",(int(RetCom),Equip))
            if Equip == 'Vent':
                print ('Pomyślna aktualizacja {0}'.format(Equip))
            else:
                print ('Pomyślna aktualizacja {0}'.format(Equip))
            break
        except:
                print ('Equip error')
                break
    db.commit()
    #print("comit Stan")
    CloseDB(db)
#----------------------------------------------zerowanie bazy danych na poczatku programu--------------
def zerowanieDB():
    db = ConnectDB() #otwarcie
    curs = db.cursor()

    curs.execute ("UPDATE control SET Stan='0',Liczba='0',Tryb='0',ComDev='0' WHERE Equipement='Lamp';") #wykonanie na bazie danych
    curs.execute ("UPDATE control SET Stan='0',Liczba='0',Tryb='0',ComDev='0' WHERE Equipement='Pump';") #pompa
    curs.execute ("UPDATE control SET Stan='0',Liczba='0',Tryb='0',ComDev='0' WHERE Equipement='Vent';")
    curs.execute ("UPDATE control SET Stan='0',Liczba='0',Tryb='0',ComDev='0' WHERE Equipement='Heat';") #ventylator

    curs.execute ("UPDATE sensors SET setPoint='22',DeltaT='2' WHERE Sensor='Temp_int';")
    curs.execute ("UPDATE sensors SET lowLevel='20',heightLevel='60' WHERE Sensor='Humidity';")

    curs.execute ("TRUNCATE TABLE data") # usunięcie danych z tabeli
    
    ser.write('CPRESET') # write a string
    db.commit() # Commit your changes in the database
    CloseDB(db) #zamkniecie bazy dancy

#----------------------------------------------------------------------------------------FUNKCJA ZCZYTUJACA TEMP, HUMID, LUMIN

def MajDBMesures(Commande,Mesure):
        db = ConnectDB()
        curs = db.cursor()
        ValId=0
        now = time.strftime('%Y-%m-%d %H-%M-%S')
        
        if Mesure == 'Temp_int':
            ValId=1
            print("valId: ", ValId)
        elif Mesure == 'Lumin':
            ValId=2
            print("valId: ", ValId)
        elif Mesure == 'Humidity':
            ValId=3
            print("valId: ", ValId)
        while True:
            try:
                #while True:
                    #print('true...')
                    ser.write(Commande)
                    time.sleep(0.1)
                    print('comande: ', Commande)
                    Vcom=str(ser.readline().strip().decode("UTF-8"))
                    print(type(Vcom))
                    print("Vcom0: ", Vcom)
                    if Vcom == '0' or Vcom == "": break
                    #if not Vcom=="": break
                    # print('Retcom2: ', Retcom2)
                    
                
                    curs.execute("INSERT INTO data(IdType,Date,Value) VALUES(%s,%s,%s);",(ValId, now, Vcom))
                    #time.sleep(1)
                    if ValId==3:
                            print ('rejestracja {0}'.format(Mesure))
                            print(Vcom)
                    else:
                            print ('rejestracja {0}'.format(Mesure))
                            print(Vcom)
                    if Vcom!=0:
                            break
            except mysql.connector.Error as error:
                print("Failed to insert record into DATA table {}".format(error))
                break
        

        db.commit()
        CloseDB(db)
	ser.flush()
	#ser.close()

#----------------------------------------------------------------------------------------FUNCJA ZCZYTUJACA CYKLE

def MajCounter(Commande,Equip): #aktualizowanie ile razy był włączony wentylator
    db = ConnectDB()
    curs = db.cursor()
    
    while True:
        try:
            ser.write(Commande) # send  comment to arduino 
            time.sleep(0.25)
            RetCom=int(ser.readline().strip().decode("UTF-8")) #recive code from arduino
            time.sleep(2)

            curs.execute("UPDATE control SET Liczba=%s WHERE Equipement=%s;",(RetCom,Equip))
            if Equip == 'Vent':
                print ('aktualizacja licznika {0}'.format(Equip))
            else:
                print ('aktualizacja licznika nieudana {0}'.format(Equip))
            break
        except:
            if Equip == 'Vent':
                print ('aktualizacja licznika {0}'.format(Equip))
            else:
                print ('aktualizacja licznika {0}'.format(Equip))
            break
    db.commit()
    CloseDB(db) 

#-----------------------------------------------Funkcja odczytu typów w bazie danych - pompa i wilgotność
    
def readTypeDB():
     
        db = ConnectDB()

        curs = db.cursor()

        query = """SELECT * FROM sensors where Sensor = "Humidity" """

        curs.execute (query)

        myresult = curs.fetchall()

        rowcount = curs.rowcount

        for row in myresult:
                #print("row", row)
                lowLevelHum = row[3]
                heighLevelHum = row[4]
                
                    
        query = """SELECT * FROM sensors where Sensor = "Temp_int" """       
        
        curs.execute (query)

        myresult = curs.fetchall()

        rowcount = curs.rowcount

        for row in myresult:
                #print("row", row)
                SPTemp = row[0]
                DeltaTemp = row[1] 


        CloseDB(db)

        return SPTemp,DeltaTemp,lowLevelHum,heighLevelHum

#------------------------------------------------------------------------Wykrywanie zmiany stanu danych typu --------------------------------------- 

def DetectionFrontType():

    ACK='' #Arduino serial Monitor
    SPTempPrec = 0 
    DeltaTempPrec = 0 
    lowLevelHumPrec = 0 
    highLevelHumPrec = 0
    SPTempActu,DeltaTempActu,lowLevelHumActu,highLevelHumActu = readTypeDB()
    print("SPTempPrec", SPTempPrec)
    time.sleep(2)
    print("SPTempActu", SPTempActu)
    time.sleep(2)
    
    if SPTempActu > SPTempPrec:
        while True: 
            try:
		print("zmiana temperatury aktualnej")
		print("SPTempPrec:", SPTempPrec)
                ser.write("TEMMO%s#"%SPTempActu)
                time.sleep(0.25)
                ACK=str(ser.readline().strip().decode("UTF-8"))
		print("ACCK: ", ACK)
                if ACK=='OK': break
            except:
                ''''''
        print ("TEMMO%s#"%SPTempActu)
        ACK=''
    if DeltaTempActu > DeltaTempPrec:
        while True: 
            try:
		print("zmiana delta temperatury aktualnej")
                ser.write("DELTAT%s#"%DeltaTempActu)
                time.sleep(0.25)
                ACK=str(ser.readline().strip().decode("UTF-8"))
		print("ACCK: ", ACK)
                if ACK=='OK': break
            except:
                ''''''
        print ("DELTAT%s#"%DeltaTempActu)
        ACK=''
    if lowLevelHumActu > lowLevelHumPrec:
        while True: # 
            try:
		print("zmiana humu aktualnej")
                ser.write("HUMBS%s#"%lowLevelHumActu)
                time.sleep(0.25)
                ACK=str(ser.readline().strip().decode("UTF-8"))
		print("ACCK: ", ACK)
                if ACK=='OK': break
            except:
                ''''''
        print ("HUMBS%s#"%lowLevelHumActu)
        ACK=''
    if highLevelHumActu > highLevelHumPrec:
        while True:
            try:
		print("HUMHT", highLevelHumActu)
                ser.write("HUMHT%s#"%highLevelHumActu)
                time.sleep(0.25)
                ACK=str(ser.readline().strip().decode("UTF-8"))
		        #print("ACCK: ", ACK)
                if ACK=='OK': break
            except:
                ''''''
        print ("HUMHT%s#"%highLevelHumActu)
        ACK=""
        
    return SPTempActu,DeltaTempActu,lowLevelHumActu,highLevelHumActu


#---------------------------------------------------------------OBSŁUGA LAMP----------------------------------------------------

def lampOn():
    while True:
    	try:
            ser.write("LAMPEON") # send  comment to arduino 
            time.sleep(0.25)
            RetCom=str(ser.readline().strip().decode("UTF-8")) #recive code from arduino
            print("RRR", RetCom)
            if RetCom=='OK': break
               #break
                
                 
    	except:
            break
 
def lampOff():
    while True:
    	try:
            ser.write("LAMPEOFF") # send  comment to arduino 
            time.sleep(0.25)
            RetCom=str(ser.readline().strip().decode("UTF-8")) #recive code from arduino		
            print("ACK:", ACK)		
            if RetCom=='OK': break
                #print("wyl lampy")
            #break
                            
    	except:
    		break
 
            
def Lamp():
    while True:
        nowt = datetime.datetime.now()
        print(nowt)
        time.sleep(2)
        today8am = nowt.replace(hour=8, minute=0, second=0, microsecond=000000)
        today17pm = nowt.replace(hour=17, minute=0, second=0, microsecond=000000)
        if nowt >= today8am and nowt <= today17pm:    
            lampOn()
            break
        else:
            lampOff()
            break    