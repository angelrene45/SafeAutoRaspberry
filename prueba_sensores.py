#///////////////////////////LIBRERIAS SENSORES
import RPi.GPIO as GPIO
import time
from time import sleep
import signal
from threading import Thread
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import urllib2 #Validar la conexion a internet

#Variables
MAC = "2C:3A:E8:06:F6:D4" #MAC FROM NODEMCU THAT USER LISTENER
PAHT_CRED = '/home/pi/iot/cred.json'
URL_DB = 'https://safeauto-65aa8.firebaseio.com/'
REF_SENSOR_PRESENCE = 'devices/'+MAC+'/sensors/weight'
REF_SENSOR_IMPACT = 'devices/'+MAC+'/sensors/impact'
SUCCESS_CODE = 100
ERROR_CODE = 200

#////////////////////////////////////////////////////////////
#   CONFIGURACION DE LOS PINES GPIO MODO BCM O BOARD
GPIO.setmode(GPIO.BCM)          #ASIGNACION SEGUN NOMBRE DE LOS GPIO
#GPIO.setmode(GPIO.BOARD) #PIN FISICO DE LA PLACA
GPIO.setwarnings(False)
#////////////////////////////////////////////////////////////
#   DECLARACION DE PINES Y CONFIGURACION
#ENTRADAS   nombre=NUMERO DE GPIO
sensor_impact=27
sensor_presence=4

GPIO.setup(sensor_impact,GPIO.IN)
GPIO.setup(sensor_presence,GPIO.IN)

#SALIDAS
led_impact=3
led_presence=17
GPIO.setup(led_impact,GPIO.OUT)
GPIO.setup(led_presence,GPIO.OUT)
#////////////////////////////////////////////////////////////
#   VARIABLES

#////////////////////////////////////////////////////////////
#   INICIO
GPIO.output(led_impact,0)
GPIO.output(led_presence,0)
#////////////////////////////////////////////////////////////

#//////////////////////////////////Function milisecond///////////////////////////////////////////////
current_milli_time = lambda: int(round(time.time()*1000)) #function work like millis like arduino
#////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////var for sensor presence///////////////////////////////////////////
lastPresenceTime = 0 # Record the time that we measured a shock
presenceAlarmTime = 500 # Number of milli seconds to keep the knock alarm high
presenceAlarm = False
#////////////////////////////////////////////////////////////////////////////////////////////////////

#//////////////////////////////////var for sensor impact///////////////////////////////////////////
lastImpactTime = 0 # Record the time that we measured a shock
impactAlarmTime = 500 # Number of milli seconds to keep the knock alarm high
impactAlarm = False
#//

class IOT():
#################################################Constructor##########################################################
    def __init__(self):
        cred = credentials.Certificate(PAHT_CRED)
        #Instance to Firebase Realtime DataBase and Firebase Storage
        firebase_admin.initialize_app(cred, {
            'databaseURL': URL_DB
        })
        self.refPresence = db.reference(REF_SENSOR_PRESENCE)
        self.refImpact = db.reference(REF_SENSOR_IMPACT)


#########################################################lISTENER PRESENCIA ########################################################
    def statusSensores(self):
        global lastPresenceTime
        global presenceAlarmTime
        global presenceAlarm

        global lastImpactTime
        global impactAlarmTime
        global impactAlarm

        #check the conection to Internet
        #checkConection = False
        #while checkConection == False:
            #checkConection = self.internet_on()
            #sleep(1)

        while True:
            #///////////////////////////////////////////////Sensor presence/////////////////////////////////////////
            presenceValue = GPIO.input(sensor_presence)
            if presenceValue == 0:
                lastPresenceTime = current_milli_time() # record the time of the presence
                if presenceAlarm == False:
                    print("Presence presence")
                    self.refPresence.set(0)
                    GPIO.output(led_presence,1)
                    presenceAlarm = True
            else:
                #validate on a range of 500 milisecond that the presence sensor has activity
                if (current_milli_time()-lastPresenceTime) > presenceAlarmTime and presenceAlarm :
                    print("No presence")
                    self.refPresence.set(1)
                    presenceAlarm = False
                    GPIO.output(led_presence,0)
            #//////////////////////////////////////////////////////////////////////////////////////////////////////////

            #///////////////////////////////////////////////Sensor Impacto///////////////////////////////////////////
            impactValue = GPIO.input(sensor_impact)
            if impactValue == 0:
                lastImpactTime = current_milli_time() # record the time of the presence
                if impactAlarm == False:
                    print("Impact impact")
                    self.refImpact.set(1)
                    GPIO.output(led_impact,1)
                    impactAlarm = True
            else:
                #validate on a range of 500 milisecond that the impact sensor has activity
                if (current_milli_time()-lastImpactTime) > impactAlarmTime and impactAlarm :
                    print("No impact")
                    self.refImpact.set(0)
                    impactAlarm = False
                    GPIO.output(led_impact,0)

#################################################Validate connection to Internet##############################
    def internet_on(self):
        try:
            urllib2.urlopen('http://216.58.192.142/', timeout=1)
            print("Connection successfully")
            return True
        except urllib2.URLError as err:
            print("Erro to connect")
            return False


######################################################## Main ######################################################################
print ('START !')
iot = IOT()
################### THREAD 1 #########################################
subprocess_sensors = Thread(target=iot.statusSensores)
subprocess_sensors.daemon = True
subprocess_sensors.start()

signal.pause()
