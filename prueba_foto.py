#////////////////////////////////////////////////////////////
import sys
from time import sleep
import signal
from threading import Thread
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import subprocess
import os

#Firebase Storage
from PIL import Image
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

#Camera raspberry
from picamera import PiCamera
import datetime

#GPIO
import RPi.GPIO as GPIO
import time                #Importamos time para poder usar time.sleep

#Variables
cdm_take_photo = "./webcam.sh" # command that execute the script that take the photo
cmd_stop_video = "sudo service motion stop" # command that execute the script that to stop the live stream webcam
cmd_start_video = "sudo service motion start" # command that execute the script for initialize the live stream webcam
PAHT_CRED = '/home/pi/iot/cred.json'
URL_DB = 'https://safeauto-65aa8.firebaseio.com/'
REF_CAMERA_STATUS = 'devices/2C:3A:E8:06:F6:D4/camera/status'
REF_CAMERA_PHOTOS = 'devices/2C:3A:E8:06:F6:D4/camera/photos'
REF_CAMERA = 'devices/2C:3A:E8:06:F6:D4/camera'
REF_VIDEO_STATUS = 'devices/2C:3A:E8:06:F6:D4/video/status'
REF_VIDEO = 'devices/2C:3A:E8:06:F6:D4/video'
SUCCESS_CODE = 100
ERROR_CODE = 200

REF_STATUS_DOOR = 'devices/2C:3A:E8:06:F6:D4/door/status'
#////////////////////////////////////////////////////////////
#   CONFIGURACION DE LOS PINES GPIO MODO BCM O BOARD
GPIO.setmode(GPIO.BCM)          #ASIGNACION SEGUN NOMBRE DE LOS GPIO
#GPIO.setmode(GPIO.BOARD) #PIN FISICO DE LA PLACA
GPIO.setwarnings(False)

servo_door=9
GPIO.setup(servo_door,GPIO.OUT)    #Ponemos el GPIO 9 como salida

p = GPIO.PWM(9,50)        #Ponemos el GPIO 9 en modo PWM y enviamos 50 pulsos por segundo
p.start(7.5)              #Enviamos un pulso del 7.5% para centrar el servo


class IOT():
#################################################Constructor##########################################################
    def __init__(self):
        cred = credentials.Certificate(PAHT_CRED)
        #Instance to Firebase Realtime DataBase and Firebase Storage
        firebase_admin.initialize_app(cred, {
            'databaseURL': URL_DB,
            'storageBucket': 'safeauto-65aa8.appspot.com'
        })
        #Var with the references on Firebase Realtime Database
        self.refMacCameraStatus = db.reference(REF_CAMERA_STATUS)
        self.refMacPhotos = db.reference(REF_CAMERA_PHOTOS)
        self.refCamera = db.reference(REF_CAMERA)
        self.refVideoStatus = db.reference(REF_VIDEO_STATUS)
        self.refVideo = db.reference(REF_VIDEO)
        self.camera = PiCamera()
        self.refStatusDoor = db.reference(REF_STATUS_DOOR)

#################################################Methods Camera Listener ##########################################################
    def changeStatusPhoto(self, estado):
        if estado:
            try:
                print('TAKING FOTO')

                name = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                full_path = '/home/pi/iot/photos/'+name+'.jpg'

                self.camera.resolution = (640, 360)
                self.camera.start_preview()
                sleep(2)
                self.camera.capture(full_path)
                self.camera.stop_preview()

                reference = '2C:3A:E8:06:F6:D4/'+name

                #create a bucket for storage files on Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(reference)
                outfile=full_path
                blob.upload_from_filename(outfile) #upload image to Storage
                blob.make_public() #Make public thhe image
                #set de public url that upload on firebase Storage
                self.refMacPhotos.push({
                    'url' : blob.public_url,
                    'reference' : reference
                })
                #update status on camera reference
                self.refCamera.update({
                    'status' : False
                })
                print("ok")

            except Exception as e:
                print(e)

        else:

            print('DONT NEED TO TAKE PHOTO')

#################################################Methods Video Listener ##########################################################
    def changeStatusVideo(self, estado):
        if estado:
            print('Starting Camera....')

            sudoPassword = 'batman14'
            command = 'service motion start'
            p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))

            print("Camera initialize")

            print("ok")

        else:

            print('Stoping Live Video ....')

            sudoPassword = 'batman14'
            command = 'service motion stop'
            p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))

            print("Live video has been stopped")

#################################################Methods Door Listener ##########################################################
    def changeStatusDoor(self, estado):
        if estado:
            try:
                print('Door open')

                p.ChangeDutyCycle(4.5)    #Enviamos un pulso del 4.5% para girar el servo hacia la izquierda
                time.sleep(3)           #pausa de medio segundo

                print("ok")

            except Exception as e:
                print(e)

        else:

            p.ChangeDutyCycle(10.5)   #Enviamos un pulso del 10.5% para girar el servo hacia la derecha
            time.sleep(3)           #pausa de medio segundo

            print('Door closed')


#########################################################lISTENER CAMERA STATUS ########################################################
    def statusFoto(self):
        E, i = [], 0
        estado_anterior = self.refMacCameraStatus.get()
        self.changeStatusPhoto(estado_anterior)
        E.append(estado_anterior)
        while True:
          estado_actual = self.refMacCameraStatus.get()
          E.append(estado_actual)
          if E[i] != E[-1]:
              self.changeStatusPhoto(estado_actual)
          del E[0]
          i = i + i
          sleep(0.4)
#########################################################lISTENER VIDEO STATUS ########################################################
    def statusVideo(self):
        H, j = [], 0
        estado_anterior = self.refVideoStatus.get()
        self.changeStatusVideo(estado_anterior)
        H.append(estado_anterior)
        while True:
          estado_actual = self.refVideoStatus.get()
          H.append(estado_actual)
          if H[j] != H[-1]:
              self.changeStatusVideo(estado_actual)
          del H[0]
          j = j + j
          sleep(0.4)

#################################################Status servo door#############################################
    def statusDoor(self):
      H, j = [], 0
      estado_anterior = self.refStatusDoor.get()
      self.changeStatusDoor(estado_anterior)
      H.append(estado_anterior)
      while True:
        estado_actual = self.refStatusDoor.get()
        H.append(estado_actual)
        if H[j] != H[-1]:
            self.changeStatusDoor(estado_actual)
        del H[0]
        j = j + j
        sleep(0.4)



######################################################## Main ######################################################################
print ('START !')
iot = IOT()

################### THREAD 1 #########################################
subproceso_foto = Thread(target=iot.statusFoto)
subproceso_foto.daemon = True
subproceso_foto.start()

sleep(1)

################### THREAD 2 #########################################
subproceso_video = Thread(target=iot.statusVideo)
subproceso_video.daemon = True
subproceso_video.start()

################### THREAD 3 #########################################
try:
    subprocess_door = Thread(target=iot.statusDoor)
    subprocess_door.daemon = True
    subprocess_door.start()
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()


signal.pause()
