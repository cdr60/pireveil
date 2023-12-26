#!/usr/bin/python3
from configparser import ConfigParser
import os
import time
import datetime
import LCD_Config
import LCD_1in44
import adafruit_dht
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import json
import subprocess
import sys
import threading

#apt-get install python3-numpy
#apt-get install python3-rpi.gpio
#apt-get install python3-spidev
#apt-get install python3-pil
#apt install ttf-mscorefonts-installer
#pip3 install adafruit-circuitpython-ds1307 --break-system-packages
#pip3 install adafruit-circuitpython-dht --break-system-packages
import board
import adafruit_ds1307

def printcurrentdatetime():
	now = datetime.datetime.now()
	current_time = now.strftime("%d/%m/%Y %H:%M:%S")
	print(current_time)
	

def get_dht(sensor):
	try:
		temp = sensor.temperature
		humidity = sensor.humidity
	except:
		temp,humidity=None,None
	return temp,humidity

def starting_rtc():
	i2c = board.I2C()
	rtc = adafruit_ds1307.DS1307(i2c)
	t = rtc.datetime
	s = datetime.datetime.now()
	print("RTC TIME")
	print(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
	print("SYSTEM TIME")
	print(s.year, s.month, s.day, s.hour, s.minute, s.second)
	
	if (t.tm_year==2000):
		print("Maj heure RTC a partir de l'heure systeme")
		rtc.datetime=time.struct_time((s.year, s.month, s.day, s.hour, s.minute, s.second,0,0,0))
	elif (s.year<=2000):
		print("Maj heure systeme a partir de l'heure RTC")
		time_tuple = ( t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec , 0)
		import ctypes
		import ctypes.util
		CLOCK_REALTIME = 0
		class timespec(ctypes.Structure):
			_fields_ = [("tv_sec", ctypes.c_long),("tv_nsec", ctypes.c_long)]
		librt = ctypes.CDLL(ctypes.util.find_library("rt"))
		ts = timespec()
		ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
		ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond
		librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


######################################################
# Lecture du fichier Ini de parametrage de l'alarme
######################################################
def initdata():
	#Initialisation data avec valeurs initiales
	data={}
	data["alarme"]={"heure":"00:00","duree":"1","active":"0","beepindex":"","radioindex":"","fileindex":""}
	data["audio"]={"beepindex":"","radioindex":"","fileindex":""}
	data["click"]={"short":"200","long":"1000"}
	data["color"]={"font_1_d":"#A4A4A4","font_1_n":"#939393","font_2_d":"#D4D4D4","font_2_n":"#C3C3C3","ico_d":"#D4D4D4","ico_n":"#C3C3C3","background":"#000000"}
	return data
	
def loadjson(jsonfile):
	result=[]
	print("Lecture de "+jsonfile)
	if os.path.exists(jsonfile)==False:
		print("Fichier "+jsonfile+" absent")
		return result
		
	with open(jsonfile) as user_file:
		file_contents = user_file.read()
	try:
		result = json.loads(file_contents)
	except:
		print("Fichier "+jsonfile+" mal formé")
		result=[]
	user_file.close()
	return result

def loadini(ficini,alarmelist,radiolist,audiolist):
	data=initdata()
	print("Lecture de "+ficini)
	if os.path.exists(ficini)==False:
		print("Fichier absent")
	parser = ConfigParser()	
	parser.read(ficini)
	if parser.has_section("alarme")==False: parser.add_section("alarme") 
	if parser.has_section("audio")==False: parser.add_section("audio") 
	if parser.has_section("click")==False: parser.add_section("click") 
	if parser.has_section("color")==False: parser.add_section("color") 
	#######################################################
	# COULEUR DE LA FONT DU TEXTE 1 DE JOUR (GROS TEXTES)
	#######################################################
	if (parser.has_option("color", "font_1_d")):
		ss=parser.get("color", "font_1_d")
		if (ss[0]!="#"): ss="#A4A4A4"
		if (len(ss)!=7): ss="#A4A4A4"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#A4A4A4"
		data["color"]["font_1_d"]=str(ss)
	else: parser.set("color","font_1_d",data["color"]["font_1_d"])
	
	#######################################################
	# COULEUR DE LA FONT DU TEXTE 1 DE NUIT (GROS TEXTES)
	#######################################################
	if (parser.has_option("color", "font_1_n")):
		ss=parser.get("color", "font_1_n")
		if (ss[0]!="#"): ss="#C3C3C3"
		if (len(ss)!=7): ss="#C3C3C3"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#C3C3C3"
		data["color"]["font_1_n"]=str(ss)
	else: parser.set("color","font_1_n",data["color"]["font_1_n"])

	###########################################################
	# COULEUR DE LA FONT DU TEXTE 2 DE JOUR (PETITS TEXTES)
	###########################################################
	if (parser.has_option("color", "font_2_d")):
		ss=parser.get("color", "font_2_d")
		if (ss[0]!="#"): ss="#D4D4D4"
		if (len(ss)!=7): ss="#D4D4D4"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#D4D4D4"
		data["color"]["font_2_d"]=str(ss)
	else: parser.set("color","font_2_d",data["color"]["font_2_d"])

	###########################################################
	# COULEUR DE LA FONT DU TEXTE 2 DE NUIT (PETITS TEXTES)
	###########################################################
	if (parser.has_option("color", "font_2_n")):
		ss=parser.get("color", "font_2_n")
		if (ss[0]!="#"): ss="#C3C3C3"
		if (len(ss)!=7): ss="#C3C3C3"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#C3C3C3"
		data["color"]["font_2_n"]=str(ss)
	else: parser.set("color","font_2_n",data["color"]["font_2_n"])	
	
	#############################################
	# COULEUR DES ICONES DE JOUR
	#############################################
	if (parser.has_option("color", "ico_d")):
		ss=parser.get("color", "ico_d")
		if (ss[0]!="#"): ss="#D4D4D4"
		if (len(ss)!=7): ss="#D4D4D4"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#D4D4D4"
		data["color"]["ico_d"]=str(ss)
	else: parser.set("color","ico_d",data["color"]["ico_d"])

	#############################################
	# COULEUR DES ICONES DE NUIT
	#############################################
	if (parser.has_option("color", "ico_n")):
		ss=parser.get("color", "ico_n")
		if (ss[0]!="#"): ss="#C3C3C3"
		if (len(ss)!=7): ss="#C3C3C3"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#C3C3C3"
		data["color"]["ico_n"]=str(ss)
	else: parser.set("color","ico_n",data["color"]["ico_n"])

	#############################################
	# COULEUR DU FOND D'ECRAN
	#############################################
	if (parser.has_option("color", "background")):
		ss=parser.get("color", "background")
		if (ss[0]!="#"): ss="#000000"
		if (len(ss)!=7): ss="#000000"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#000000"
		data["color"]["background"]=str(ss)
	else: parser.set("color","background",data["color"]["background"])
	
	#############################################
	# DUREE DU CLICK COURT EN MILLISECONDES
	#############################################
	if (parser.has_option("click", "short")):
		ss=parser.get("click", "short")
		s=1
		try:
			s=int(ss)
		except:
			s=200
		if s<5: s=200
		data["click"]["short"]=str(s)
	else: parser.set("click","short",data["click"]["short"])
	#############################################
	# DUREE DU CLICK LONG EN MILLISECONDES
	#############################################
	if (parser.has_option("click", "long")):
		ss=parser.get("click", "long")
		s=1
		try:
			s=int(ss)
		except:
			s=1000
		if s<int(data["click"]["short"]): data["click"]["long"]=str(int(data["click"]["short"])+500)
	else: parser.set("click","long",data["click"]["long"])
	
	#############################################
	# ALARME DU REVEIL ACTIVE OU PAS
	#############################################
	if (parser.has_option("alarme", "active")):
		try:
			x=int(parser.get("alarme", "active"))
		except:
			x=0
		if (x<0 or x>1): x=0
		data["alarme"]["active"]=str(x)
	else: parser.set("alarme","active",data["alarme"]["active"])
	#############################################
	# HEURE DU REVEIL
	#############################################
	if (parser.has_option("alarme", "heure")):
		tb=parser.get("alarme", "heure").split(":")
		h,m=0,0
		if len(tb)>0:
			try:
				h=int(tb[0])
			except:
				h=0
		if len(tb)>1:
			try:
				m=int(tb[1])
			except:
				m=0
		if (h<0) or (h>23): h=0
		if (m<0) or (m>59): m=0
		data["alarme"]["heure"]="{:02}".format(h)+":"+"{:02}".format(m)
	else: parser.set("alarme","heure",data["alarme"]["heure"])
	#############################################
	# DUREE DU REVEIL EN MINUTES
	#############################################
	if (parser.has_option("alarme", "duree")):
		sm=parser.get("alarme", "duree")
		m=1
		try:
			m=int(sm)
		except:
			m=1
		if m<1: m=1
		data["alarme"]["duree"]=m
	else: parser.set("alarme","duree",data["alarme"]["duree"])
	
	if (parser.has_option("alarme", "active")):
		try:
			x=int(parser.get("alarme", "active"))
		except:
			x=0
		if (x<0 or x>1): x=0
		data["alarme"]["active"]=str(x)
	else: parser.set("alarme","active",data["alarme"]["active"])
	#############################################
	# BEEP CHOISIS POUR LE REVEIL
	#############################################
	if (parser.has_option("alarme", "beepindex")):
		try:
			x=int(parser.get("alarme", "beepindex"))
		except:
			x=None
		if x!=None: 
			if (x<0) or (x>len(alarmelist)-1): x=None
		if x!=None: data["alarme"]["radioindex"]=str(x)
	else: parser.set("alarme","beepindex",data["alarme"]["beepindex"])
	#############################################
	# STATION RADIO CHOISIS POUR LE REVEIL
	#############################################
	if (parser.has_option("alarme", "radioindex")):
		try:
			x=int(parser.get("alarme", "radioindex"))
		except:
			x=None
		if x!=None: 
			if (x<0) or (x>len(radiolist)-1): x=None
		if x!=None: data["alarme"]["radioindex"]=str(x)
	else: parser.set("alarme","radioindex",data["alarme"]["radioindex"])
	#############################################
	# FICHIER AUDIO CHOISIS POUR LE REVEIL
	#############################################
	if (parser.has_option("alarme", "fileindex")):
		try:
			x=int(parser.get("alarme", "fileindex"))
		except:
			x=None
		if x!=None: 
			if (x<0) or (x>len(audiolist)-1): x=None
		if x!=None: data["alarme"]["fileindex"]=str(x)
	else: parser.set("alarme","fileindex",data["alarme"]["fileindex"])

	#############################################
	# BEEP A ECOUTER HORS REVEIL
	#############################################
	if (parser.has_option("audio", "beepindex")):
		try:
			x=int(parser.get("audio", "beepindex"))
		except:
			x=None
		if x!=None:
			if (x<0) or (x>len(alarmelist)-1): x=None
		if x!=None: data["audio"]["beepindex"]=str(x)
	else: parser.set("audio","beepindex",data["audio"]["beepindex"])
			
	#############################################
	# RADIO A ECOUTER HORS REVEIL
	#############################################
	if (parser.has_option("audio", "radioindex")):
		try:
			x=int(parser.get("audio", "radioindex"))
		except:
			x=None
		if x!=None:
			if (x<0) or (x>len(radiolist)-1): x=None
		if x!=None: data["audio"]["radioindex"]=str(x)
	else: parser.set("audio","radioindex",data["audio"]["radioindex"])
	
	#############################################
	# AUDIO A ECOUTER HORS REVEIL
	#############################################
	if (parser.has_option("audio", "fileindex")):
		try:
			x=int(parser.get("audio", "fileindex"))
		except:
			x=None
		if x!=None:
			if (x<0) or (x>len(audiolist)-1): x=None
		if x!=None: data["audio"]["fileindex"]=str(x)
	else: parser.set("audio","fileindex",data["audio"]["fileindex"])
	
	if (data["alarme"]["beepindex"]=="") and (data["alarme"]["radioindex"]=="") and (data["alarme"]["fileindex"]==""):
		data["alarme"]["beepindex"]="0"
	with open(ficini, 'w') as configfile:
		parser.write(configfile)	
	return data

def saveini(data_ini,ficini):
	config = ConfigParser()
	config.read(ficini)
	config["alarme"]["heure"]=data_ini["alarme"]["heure"]
	config["alarme"]["active"]=data_ini["alarme"]["active"]
	config["alarme"]["beepindex"]=data_ini["alarme"]["beepindex"]
	config["alarme"]["radioindex"]=data_ini["alarme"]["radioindex"]
	config["alarme"]["fileindex"]=data_ini["alarme"]["fileindex"]
	config["audio"]["beepindex"]=data_ini["audio"]["beepindex"]
	config["audio"]["radioindex"]=data_ini["audio"]["radioindex"]
	config["audio"]["fileindex"]=data_ini["audio"]["fileindex"]
	config["color"]["font_1_d"]=data_ini["color"]["font_1_d"]
	config["color"]["font_1_n"]=data_ini["color"]["font_1_n"]
	config["color"]["font_2_d"]=data_ini["color"]["font_2_d"]
	config["color"]["font_2_n"]=data_ini["color"]["font_2_n"]
	config["color"]["ico_d"]=data_ini["color"]["ico_d"]
	config["color"]["ico_n"]=data_ini["color"]["ico_n"]
	config["color"]["background"]=data_ini["color"]["background"]
	with open(ficini,'w') as configfile:
		config.write(configfile)
	
####################################################################################
# OBJET CLAVIER
####################################################################################
class Keyboard(threading.Thread):
	def __init__(self, KEY_UP_PIN,KEY_DOWN_PIN,KEY_LEFT_PIN,KEY_RIGHT_PIN,KEY_PRESS_PIN,KEY_1_PIN,KEY_2_PIN,KEY_3_PIN,min_short_time=150,min_long_time=1000):
		threading.Thread.__init__(self)
		self.lock = threading.Lock()
		self.min_short_time=min_short_time/1000.00
		self.min_long_time=min_long_time/1000.00
		K_UP={"pin":KEY_UP_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_DOWN={"pin":KEY_DOWN_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_LEFT={"pin":KEY_LEFT_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_RIGHT={"pin":KEY_RIGHT_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_PRESS={"pin":KEY_PRESS_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_1={"pin":KEY_1_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_2={"pin":KEY_2_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_3={"pin":KEY_3_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		self.BUTTONS={"K_UP":K_UP,"K_DOWN":K_DOWN,"K_LEFT":K_LEFT,"K_RIGHT":K_RIGHT,"K_PRESS":K_PRESS,"K_1":K_1,"K_2":K_2,"K_3":K_3}

		GPIO.setmode(GPIO.BCM)
		for key in self.BUTTONS:
			GPIO.setup(self.BUTTONS[key]["pin"],GPIO.IN, pull_up_down=GPIO.PUD_UP)		# Input with pull-up
		self.deamon = True
		#pour démarrer le service : start mais je le fais ailleurs
		#self.start()


	def run(self):
		for key in self.BUTTONS:
			self.BUTTONS[key]["previous"]=None
			self.BUTTONS[key]["time"]=0
			self.BUTTONS[key]["pressed"]=False
			self.BUTTONS[key]["type"]=""

		while 1:
			for key in self.BUTTONS:
				self.BUTTONS[key]["current"]=GPIO.input(self.BUTTONS[key]["pin"])
				time.sleep(0.01)
				if self.BUTTONS[key]["current"]==0 and self.BUTTONS[key]["previous"]==1:
					self.BUTTONS[key]["pressed"] = True
					self.BUTTONS[key]["time"]=0
					while self.BUTTONS[key]["pressed"]:
						time.sleep(0.05)
						self.BUTTONS[key]["time"]+=0.05
						self.BUTTONS[key]["current"]=GPIO.input(self.BUTTONS[key]["pin"])
						if (self.BUTTONS[key]["current"]==1): self.BUTTONS[key]["pressed"]=False
						
				self.BUTTONS[key]["previous"] = self.BUTTONS[key]["current"]
				if self.BUTTONS[key]["time"]<self.min_short_time: self.BUTTONS[key]["type"]=""
				elif self.BUTTONS[key]["time"]>=self.min_long_time: self.BUTTONS[key]["type"]="long"
				else: self.BUTTONS[key]["type"]="short"

	def wich_btn(self):
		btn,typ=None,None
		for key in self.BUTTONS:
			if self.BUTTONS[key]["type"]!="": 
				btn,typ=key,self.BUTTONS[key]["type"]
				self.BUTTONS[btn]["type"]=""
				self.BUTTONS[btn]["pressend"]=False
				self.BUTTONS[btn]["time"]=0
				self.BUTTONS[btn]["current"]=0
				self.BUTTONS[btn]["previous"]=0
				return btn,typ
			time.sleep(0.01)
		return btn,typ

####################################################################################
# OBJET REVEIL
####################################################################################
class MonReveil():

	def __init__(self,fontfile,dht=True):
		#numéro de page initiale
		self.page=0
		#pour savoir si la page heure doit être raffraichit
		self.oldmin=-1
		#pour savoir si la page alarme doit être raffraichit
		self.refreshalarme=True
		self.ts_last_temp, self.old_temp, self.old_humidity , self.sensor, self.radiothread = None, None, None, None, None
		if (dht == True) :self.sensor = adafruit_dht.DHT11(board.D23)
		if os.path.exists(fontfile): self.fontfile=fontfile
		else: self.fontfile="/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
		#######################################
		#TAILLE ECRAN
		#######################################
		self.width = 128
		self.height = 128
		#######################################
		#GPIO PINS ECRANS (POUR MEMOIRE)
		#######################################
		self.PIN_RST=27
		self.PIN_MOSI=10
		self.PIN_MISO=9
		self.PIN_CLK=11
		self.PIN_BL=24
		self.PIN_DC=25
		self.PIN_CE0=8
		self.PIN_CE1=7
		#######################################
		#GPIO DES BOUTONS
		#######################################
		self.KEY_UP_PIN=6
		self.KEY_DOWN_PIN=19
		self.KEY_LEFT_PIN=5
		self.KEY_RIGHT_PIN=26
		self.KEY_PRESS_PIN=13
		self.KEY_1_PIN=21
		self.KEY_2_PIN=20
		self.KEY_3_PIN=16

		###################################################
		#Chargement fichier ini: descriptions des fonctionnalités
		###################################################
		self.audioplayerfilename=os.path.dirname(os.path.realpath(__file__))+"/play.py"
		self.radiolistfilename=os.path.dirname(os.path.realpath(__file__))+"/radiolist.json"
		self.radiolist=loadjson(self.radiolistfilename)
		self.alarmelistfilename=os.path.dirname(os.path.realpath(__file__))+"/alarmelist.json"
		self.alarmelist=loadjson(self.alarmelistfilename)
		for i in range(0,len(self.radiolist)):
			print("Station "+str(i)+" id:"+str(self.radiolist[i]["id"])+"  nom:"+self.radiolist[i]["name"]+"  url:"+self.radiolist[i]["url"])
		self.audiolist=loadjson(os.path.dirname(os.path.realpath(__file__))+"/audiolist.json")
		for i in range(0,len(self.audiolist)):
			print("Audio "+str(i)+" id:"+str(self.audiolist[i]["id"])+" name:"+str(self.audiolist[i]["name"])+"  filename:"+self.audiolist[i]["filename"])
		for i in range(0,len(self.alarmelist)):
			print("Audio "+str(i)+" id:"+str(self.alarmelist[i]["id"])+" name:"+str(self.alarmelist[i]["name"])+"  filename:"+self.alarmelist[i]["filename"])

		self.ficini=os.path.dirname(os.path.realpath(__file__))+"/param.ini"
		self.DATA_INI=loadini(self.ficini,self.alarmelist,self.radiolist,self.audiolist)
		print(self.DATA_INI)

		#Si le reveil sonne, le stoper automatiquement au bout de ... minutes
		self.dureealarme=int(self.DATA_INI["alarme"]["duree"])
		#Durée du click court 
		self.clickshort=int(self.DATA_INI["click"]["short"])
		#Durée du click court 
		self.clicklong=int(self.DATA_INI["click"]["long"])
		
		#####################
		#Clavier
		#####################
		self.KB=Keyboard(self.KEY_UP_PIN,self.KEY_DOWN_PIN,self.KEY_LEFT_PIN,self.KEY_RIGHT_PIN,self.KEY_PRESS_PIN,self.KEY_1_PIN,self.KEY_2_PIN,self.KEY_3_PIN,self.clickshort,self.clicklong)

		#####################################
		# INIT DISPLAY
		#####################################
		self.disp = LCD_1in44.LCD()
		Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
		self.disp.LCD_Init(Lcd_ScanDir)
		self.disp.LCD_Clear()
		img=os.path.dirname(os.path.realpath(__file__))+"/time.bmp"
		if os.path.exists(img):
			image = Image.open(img)
			self.disp.LCD_ShowImage(image,0,0)
			time.sleep(0.5)
	
	
	#Seulement dans le menu principal
	def start_stop_playing_audio(self,audio=""):
		if self.radiothread!=None:
			print("stop audio")
			self.radiothread.kill()
			self.radiothread=None
			return
		if audio=="": return
		print("start audio ")
		print(self.audioplayerfilename)
		print(audio)
		self.radiothread = subprocess.Popen([self.audioplayerfilename , audio], shell=False)
		
	def detect_2_button(self,a,b):
		sleeptime=0.01
		result=""
		if ((GPIO.input(a) == 0) and (GPIO.input(b) == 0)):
			button_press_timer = 0
			while (GPIO.input(a) == 0) and (GPIO.input(b) == 0) and (button_press_timer<self.longtime):
				time.sleep(sleeptime)
				button_press_timer += sleeptime
			if button_press_timer>=self.longtime:  result="LONG_"
			elif button_press_timer>=sleeptime:   result="SHORT_"
		if result!="":
			if a==self.KEY_1_PIN: result+="K1_"
			elif a==self.KEY_2_PIN: result+="K2_"
			elif a==self.KEY_3_PIN: result+="K3_"
			elif a==self.KEY_PRESS_PIN: result+="PRESS_"
			if b==self.KEY_1_PIN: result+="K1"
			elif b==self.KEY_2_PIN: result+="K2"
			elif b==self.KEY_3_PIN: result+="K3"
		return result

	#quelle couleur par defaut ?
	#ft="font_1" ou "font_2" oi "ico"
	def get_default_color(self,ft="font_1"):
		dt = datetime.datetime.now()
		x=dt.hour*100+dt.minute
		#jour ou nuit ?
		if (x>=1400 and x<=2200): s=ft+"_d"
		else: s=ft+"_n"
		return self.DATA_INI["color"][s]

	#petit triangle du player
	def dessine_playing(self,left=10,top=10,width=24,height=24,color="#DCDCDC"):
		########################################
		# RECTANGLE DU FOND
		########################################
		self.draw.rectangle((left , top ,left + width, top + height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])
		########################################
		# TRIANGLE DU PLAYER
		########################################
		shape = [(left , top ), (left , top + height ), (left + width, top + height//2 )] 
		self.draw.polygon(shape, outline=color, fill=color) 
			
	#preparer un affiche de pages
	def prepare_page_vierge(self):
		# CREER UNE IMAGE VIDE
		self.image = Image.new('RGB', (self.width, self.height))
		# DESSINER L'IMAGE
		self.draw = ImageDraw.Draw(self.image)
		# DESSINER UN RECTANGLE FOND INDIGO
		self.draw.rectangle((0,0,self.width,self.height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])

		#CONTOUR
		#border_color="#002951"
		#self.draw.line([(0,0),(127,0)], fill = border_color,width = 1)
		#self.draw.line([(127,0),(127,127)], fill = border_color,width = 1)
		#self.draw.line([(127,127),(0,127)], fill = border_color,width = 1)
		#self.draw.line([(0,127),(0,0)], fill = border_color,width = 1)		
		#TEXTE pour test
		myfont = ImageFont.truetype(self.fontfile, 16)
		self.draw.text((5, 5), "waveshare", fill = self.get_default_color("font_1"), font = myfont)
		myfont = ImageFont.truetype(self.fontfile, 42)
		line="00:00"
		left, top, right, bottom = myfont.getbbox(line)
		w = right - left
		h = bottom - top
		self.draw.text(((128 - w ) // 2, 30), line, fill = self.get_default_color("font_1"), font = myfont)
		self.disp.LCD_ShowImage(self.image,0,0)
		
		
	def dessine_cloche(self,underline=False,left=10,top=10,width=24,height=24,color="#DCDCDC"):
		########################################
		# FOND
		########################################
		self.draw.rectangle((left,top,left+width,top+height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])
		########################################
		# DEMI-CERCLE DU HAUT
		########################################
		coteshape= ( width // 2 )
		y=( height // 30)
		if (y==0):y=1
		shape = [(left + (width-coteshape)//2, top + y ), (left + (width-coteshape)//2 + coteshape , top + y + coteshape )] 
		self.draw.chord(shape, start = 180, end = 0, fill =color, outline =color)
		y=y+coteshape//2

		########################################
		# CORPS : RECTANGLE
		########################################
		wr=coteshape
		hr=coteshape//2
		shape = [(left + (width-wr)//2, top + y ), (left + (width-wr)//2 + coteshape , top + y + hr )] 
		self.draw.rectangle(shape, outline=color, fill=color)
		y=y+hr

		########################################
		# TRIANGLES DU BAS ET RECTANGLE
		########################################
		wt=coteshape
		ht=coteshape//2
		lt=wr//4
		shape = [(left + (width-wr)//2, top + y ), (left + (width-wr)//2 + coteshape , top + y + ht )] 
		self.draw.rectangle(shape, outline=color, fill=color)

		shape = [(left + (width-wt)//2 , top + y ), (left + (width-wt )//2 , top + y + ht ), (left + (width-wt)//2 - lt, top + y + ht )] 
		self.draw.polygon(shape, outline=color, fill=color) 
		shape = [(left + (width-coteshape)//2 + coteshape , top + y ), (left + (width-coteshape)//2 + coteshape , top + y + ht ), (left + (width-coteshape)//2 + coteshape + lt, top + y + ht )] 
		self.draw.polygon(shape, outline=color, fill=color) 
		y=y+ht

		########################################
		# PETIT DEMI-CERCLE EN BAS
		########################################
		taillecercle= coteshape // 4
		shape = [(left + (width-taillecercle)//2, top + y ), (left + (width-taillecercle)//2 + taillecercle , top + y + taillecercle )] 
		self.draw.chord(shape, start = 0, end = 180, fill =color, outline =color)
		y=y+taillecercle // 2
	
		#######################################
		# SOUS-LIGNER
		#######################################
		if (underline==True):
			shape = [(left + taillecercle , top + height), (left + width - taillecercle, top + height )] 
			self.draw.line(shape, fill=color, width=2, joint=None)
			
	def dessine_radio(self,underline=False,left=10,top=10,width=24,height=24,color="#DCDCDC"):
		########################################
		# FOND
		########################################
		self.draw.rectangle((left,top,left+width,top+height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])
		########################################
		# CERCLE CENTRALE
		########################################
		taillepoint= width // 8
		y=0
		shape = [(left + (width-taillepoint)//2, top + y + (height - taillepoint)//2 ), (left + (width-taillepoint)//2 + taillepoint , top + y + height - (height - taillepoint)//2 )] 
		self.draw.chord(shape, start = 0, end = 360, fill =color, outline =color)

		########################################
		# 1ER ARCS DE CERCLES
		########################################
		taillecercle1= taillepoint + width // 3 
		shape = [(left + (width-taillecercle1)//2, top + y + (height - taillecercle1)//2 ), (left + (width-taillecercle1)//2 + taillecercle1 , top + y + height - (height - taillecercle1)//2 )] 
		self.draw.arc(shape, start = -60, end = 60, fill =color, width = 2)
		self.draw.arc(shape, start = 120, end = 240, fill =color, width = 2)
		
		########################################
		# 2iEME ARCS DE CERCLES
		########################################
		taillecercle2= taillecercle1 +  width // 3
		shape = [(left + (width-taillecercle2)//2, top + y + (height - taillecercle2)//2 ), (left + (width-taillecercle2)//2 + taillecercle2 , top + y + height - (height - taillecercle2)//2 )] 
		self.draw.arc(shape, start = -60, end = 60, fill =color, width = 2)
		self.draw.arc(shape, start = 120, end = 240, fill =color, width = 2)
		
		#######################################
		# SOUS-LIGNER
		#######################################
		if (underline==True):
			shape = [(left + taillecercle2 , top + height), (left + width - taillecercle2, top + height )] 
			self.draw.line(shape, fill=color, width=2, joint=None)


	def dessine_note(self,underline=False,left=10,top=10,width=24,height=24,color="#DCDCDC"):
		########################################
		# FOND
		########################################
		self.draw.rectangle((left,top,left+width,top+height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])
		########################################
		# POINTS 1 ET 2 DE LA CROCHE
		########################################
		taillepoint= width // 4
		shape = [(left + width//5 - taillepoint // 2, top + 6 * height // 8 - taillepoint // 2 ), (left + width//5 + taillepoint // 2 ,top + 6 * height // 8 + taillepoint // 2 )] 
		self.draw.chord(shape, start = 0, end = 360, fill =color, outline =color)

		shape = [(left + 3 * width // 4 - taillepoint // 2 , top + 5 * height // 8 - taillepoint // 2 ), (left + 3 * width // 4 + taillepoint // 2 , top + 5 * height // 8 + taillepoint // 2 )] 
		self.draw.chord(shape, start = 0, end = 360, fill =color, outline =color)

		########################################
		# BARRES VERTICALES
		########################################
		wr=width // 14
		hr=width // 2
		x= left + width//5 + taillepoint // 4 
		y= top + 6 * height // 8 
		A1=( x , y - hr )
		B1=( x + wr , y )
		shape = [A1,B1] 
		self.draw.rectangle(shape, outline=color, fill=color)
		x= left + 3 * width // 4 + taillepoint // 4 
		y= top + 5 * height // 8 
		A2=( x , y - hr )
		B2=( x + wr , y )
		shape = [A2,B2] 
		self.draw.rectangle(shape, outline=color, fill=color)

		########################################
		# BARRE OBLIQUE : ON UTILISE A1 ET A2
		########################################
		h=width // 12
		B1=( A1[0]  , A1[1] + h )
		B2=( A2[0]  , A2[1] + h )
		shape = [A1,A2,B2,B1]
		self.draw.polygon(shape, outline=color, fill=color, width=h)
		
		#######################################
		# SOUS-LIGNER
		#######################################
		if (underline==True):
			shape = [(left + width//5 - taillepoint // 2 , top + height), (left + 3 * width // 4 + taillepoint // 2, top + height )] 
			self.draw.line(shape, fill=color, width=2, joint=None)
	
	#Afficher la date et l'heure
	def ecran_heure(self):
		#ne rien faire si rien n'a changé
		dt = datetime.datetime.now()
		if (dt.minute==self.oldmin): return
		self.oldmin=dt.minute
		#Effacer
		self.draw.rectangle((0,0,self.width,self.height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])
		
		#CONTOUR
		#border_color="#002951"
		#self.draw.line([(0,0),(127,0)], fill = border_color,width = 1)
		#self.draw.line([(127,0),(127,127)], fill = border_color,width = 1)
		#self.draw.line([(127,127),(0,127)], fill = border_color,width = 1)
		#self.draw.line([(0,127),(0,0)], fill = border_color,width = 1)	
		
		#ICONE PLAYER
		col=self.DATA_INI["color"]["background"]
		if self.radiothread!=None: col=self.get_default_color("ico")
		self.dessine_playing(left=5,top=10,width=7,height=10,color=col)
		
		#ALARME ET RADIO
		#Cloche
		col=self.get_default_color("ico")
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["beepindex"]!=""): col="RED"
		self.dessine_cloche(underline=False,left=15,top=5,width=24,height=24,color=col)
		#Radio
		col=self.get_default_color("ico")
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["radioindex"]!=""): col="RED"
		self.dessine_radio(underline=False,left=15+25+10,top=5,width=24,height=24,color=col)
		#NOTE
		col=self.get_default_color("ico")
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["fileindex"]!=""): col="RED"
		self.dessine_note(underline=False,left=15+25+10+25+10,top=5,width=24,height=24,color=col)
		
		#HEURE  ET DATE
		WEEKDAYS= ['Dim', 'Lun','Mar','Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
		MONTHS=['', 'Jan','Fev','Mars','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc'];
		dt = datetime.datetime.now()
		#TEXTE pour heure
		myfont = ImageFont.truetype(self.fontfile, 42)
		line="{:02}".format(dt.hour)+":"+"{:02}".format(dt.minute)
		left, top, right, bottom = myfont.getbbox(line)
		w = right - left
		h = bottom - top
		y=25
		self.draw.text(((128 - w ) // 2, y), line, fill = self.get_default_color("font_1") , font = myfont)
		y+=h+15
		#TEXTE pour date
		myfont = ImageFont.truetype(self.fontfile, 14)
		line=WEEKDAYS[dt.isoweekday()]+" {:02}".format(dt.day)+" "+MONTHS[dt.month]+" {:04}".format(dt.year)
		left, top, right, bottom = myfont.getbbox(line)
		w = right - left
		h = bottom - top
		#Ecrire
		self.draw.text(((128 - w ) // 2, y), line, fill = self.get_default_color("font_2") , font = myfont)
		y+=h+8
		
		#Temperature : toutes les 2 secondes maxi
		todo=0
		if (self.sensor!=None):
			if self.ts_last_temp==None: todo=1
			elif (datetime.datetime.now() - self.ts_last_temp).total_seconds()>2: 
				todo=1
			if (todo==1):
				self.ts_last_temp=datetime.datetime.now()
				temp,humidity=get_dht(self.sensor)
				if (temp!=None): 
					self.old_temp,self.old_humidity=temp,humidity
				else: temp,humidity = self.old_temp,self.old_humidity
			else:
				temp,humidity=self.old_temp,self.old_humidity

			if (temp!=None):
				#TEXTE pour Temperature
				myfont = ImageFont.truetype(self.fontfile, 14)
				line="{:02}".format(temp)+"°C  |  {:02}".format(humidity)+"%"
				left, top, right, bottom = myfont.getbbox(line)
				w = right - left
				h = bottom - top
				#Ecrire
				self.draw.text(((128 - w ) // 2, y), line, fill = self.get_default_color("font_2"), font = myfont)
		#si pas de sonde : heure de l'alarme si activée
		elif self.DATA_INI["alarme"]["active"]=="1":
			myfont = ImageFont.truetype(self.fontfile, 14)
			line=self.DATA_INI["alarme"]["heure"]+" "
			bs=self.DATA_INI["alarme"]["beepindex"]
			rs=self.DATA_INI["alarme"]["radioindex"]
			fs=self.DATA_INI["alarme"]["fileindex"]
			if bs!="": line+=self.alarmelist[int(bs)]["name"][0:8] 
			elif rs!="": line+=self.radiolist[int(rs)]["name"][0:8] 
			elif fs!="": line+=self.audiolist[int(fs)]["name"][0:8] 
			line=line.strip()
			left, top, right, bottom = myfont.getbbox(line)
			w = right - left
			h = bottom - top
			#Ecrire
			self.draw.text(((128 - w ) // 2, y), line, fill = self.get_default_color("font_2"), font = myfont)
		#Musique - Radio - Beep Selectionnée
		y+=h+8
		myfont = ImageFont.truetype(self.fontfile, 14)
		bs=self.DATA_INI["audio"]["beepindex"]
		rs=self.DATA_INI["audio"]["radioindex"]
		fs=self.DATA_INI["audio"]["fileindex"]
		tb=[]
		if bs!="": tb.append(self.alarmelist[int(bs)]["name"]) 
		if rs!="": tb.append(self.radiolist[int(rs)]["name"]) 
		if fs!="": tb.append(self.audiolist[int(fs)]["name"])
		if len(tb)==3:
			for i in range(0,len(tb)): tb[i]=tb[i][0:7]
		elif len(tb)==2:
			for i in range(0,len(tb)): tb[i]=tb[i][0:9]
		elif len(tb)==1:
			for i in range(0,len(tb)): tb[i]=tb[i][0:16]
		line="-".join(tb).strip()
		left, top, right, bottom = myfont.getbbox(line)
		w = right - left
		h = bottom - top
		#Ecrire
		self.draw.text(((128 - w ) // 2, y), line, fill = self.get_default_color("font_2"), font = myfont)
		self.disp.LCD_ShowImage(self.image,0,0)
		#Lancer le reveil
		audioalarme=""
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.radiothread==None) and (dt.second<5) and ("{:02}".format(dt.hour)+":"+"{:02}".format(dt.minute)==self.DATA_INI["alarme"]["heure"]):
			bs=self.DATA_INI["alarme"]["beepindex"]
			rs=self.DATA_INI["alarme"]["radioindex"]
			fs=self.DATA_INI["alarme"]["fileindex"]
			if bs!="": audioalarme=self.alarmelist[int(bs)]["filename"] 
			elif rs!="": audioalarme=self.radiolist[int(rs)]["url"] 
			elif fs!="": audioalarme=self.audiolist[int(fs)]["filename"] 
		if audioalarme!="":
			self.start_stop_playing_audio(audioalarme)

#######################################

	#arrêt auto de l'alarme au bout de n minutes
	def autostop_alarme(self):
		tb=self.DATA_INI["alarme"]["heure"].split(":")
		h=int(tb[0])
		m=int(tb[1])
		dt = datetime.datetime.now()
		dtalarme=datetime.datetime(dt.year, dt.month, dt.day, h, m, 0)
		#si le réveil était à 23h58, on est le lendemain à 0h01, il faut se replacer sur la veille
		dttest=dtalarme-datetime.timedelta(minutes=self.dureealarme)
		if dttest.day!=dtalarme.day: dtalarme=dtalarme-datetime.timedelta(days=1)
#		print(dtalarme)
		dtalarmestop1 = dtalarme + datetime.timedelta(minutes=self.dureealarme) 
#		print(dtalarmestop1)
		dtalarmestop2 = dtalarme + datetime.timedelta(minutes=self.dureealarme+1) 
#		print(dtalarmestop2)
#		time.sleep(0.1)

		if (self.DATA_INI["alarme"]["active"]=="1") and (self.radiothread!=None) and (dt>dtalarmestop1) and (dt<dtalarmestop2):
			self.start_stop_playing_audio("")
			
######################################
		
	#Afficher le menu de réglage l'alarme
	#k= curseur à régler : DH, DU, DM, UM = 0,1,2,3
	def ecran_alarme(self,k=0):
		#Si pas besoin de rafraichissement
		if self.refreshalarme!=True : return
		#Effacer
		self.draw.rectangle((0,0,self.width,self.height), outline=self.DATA_INI["color"]["background"], fill=self.DATA_INI["color"]["background"])
		
		#CONTOUR
		#border_color="#002951"
		#self.draw.line([(0,0),(127,0)], fill = border_color,width = 1)
		#self.draw.line([(127,0),(127,127)], fill = border_color,width = 1)
		#self.draw.line([(127,127),(0,127)], fill = border_color,width = 1)
		#self.draw.line([(0,127),(0,0)], fill = border_color,width = 1)	
		
		#ICONE PLAYER
		col=self.DATA_INI["color"]["background"]
		if self.radiothread!=None: col=self.get_default_color("ico")
		self.dessine_playing(left=5,top=10,width=7,height=10,color=col)

		#Cloche
		print(self.DATA_INI)
		col=self.get_default_color("ico")
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["beepindex"]!=""): col="RED"
		print("cloche "+col)
		ycloche=5
		self.dessine_cloche(underline=False,left=90,top=ycloche,width=28,height=28,color=col)
		if self.DATA_INI["alarme"]["beepindex"]!="":
			myfont = ImageFont.truetype(self.fontfile, 16)
			line=self.alarmelist[int(self.DATA_INI["alarme"]["beepindex"])]["name"][0:10]
			left, top, right, bottom = myfont.getbbox(line)
			w = right - left
			h = bottom - top
			#Ecrire
			self.draw.text(((128 - 28 - w ) // 2 , ycloche+7), line, fill = self.get_default_color("font_2"), font = myfont)
		
		#Radio
		col=self.get_default_color("ico")
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["radioindex"]!=""): col="RED"
		print("Radio "+col)
		yradio=ycloche+25
		self.dessine_radio(underline=False,left=90,top=yradio,width=28,height=28,color=col)
		if self.DATA_INI["alarme"]["radioindex"]!="":
			myfont = ImageFont.truetype(self.fontfile, 16)
			line=self.radiolist[int(self.DATA_INI["alarme"]["radioindex"])]["name"][0:10]
			left, top, right, bottom = myfont.getbbox(line)
			w = right - left
			h = bottom - top
			#Ecrire
			self.draw.text(((128 - 28 - w ) // 2 , yradio+7), line, fill = self.get_default_color("font_2"), font = myfont)

		#NOTE
		col=self.get_default_color("ico")
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["fileindex"]!=""): col="RED"
		print("Audio "+col)
		ynote=yradio+25
		self.dessine_note(underline=False,left=90,top=ynote,width=28,height=28,color=col)
		if self.DATA_INI["alarme"]["fileindex"]!="":
			myfont = ImageFont.truetype(self.fontfile, 16)
			line=self.audiolist[int(self.DATA_INI["alarme"]["fileindex"])]["name"][0:10]
			left, top, right, bottom = myfont.getbbox(line)
			w = right - left
			h = bottom - top
			#Ecrire
			self.draw.text(((128 - 28 - w ) // 2 , ynote+7), line, fill = self.get_default_color("font_2"), font = myfont)

		#HEURE DE L'ALARME
		DH=self.DATA_INI["alarme"]["heure"][0]
		UH=self.DATA_INI["alarme"]["heure"][1]
		SEP=self.DATA_INI["alarme"]["heure"][2]
		DM=self.DATA_INI["alarme"]["heure"][3]
		UM=self.DATA_INI["alarme"]["heure"][4]
		myfont = ImageFont.truetype(self.fontfile, 30)
		left, top, right, bottom = myfont.getbbox("0")
		lpas = right - left
		hpas = bottom - top
		left, top, right, bottom = myfont.getbbox(":")
		seppas = right - left
		wtotal = lpas * 4 + seppas
		#Ecrire
		y=85
		xdh= (128 - 32 - wtotal ) // 2
		self.draw.text((xdh, y), DH, fill = self.get_default_color("font_2"), font = myfont)
		xuh=xdh+lpas
		self.draw.text((xuh, y), UH, fill = self.get_default_color("font_2"), font = myfont)
		xsep=xuh+lpas
		self.draw.text((xsep, y), SEP, fill = self.get_default_color("font_2"), font = myfont)
		xdm=xsep+seppas
		self.draw.text((xdm, y), DM, fill = self.get_default_color("font_2"), font = myfont)
		xum=xdm+lpas
		self.draw.text((xum, y), UM, fill = self.get_default_color("font_2"), font = myfont)
		xcur=xdh
		ycur=y+hpas+10
		if k==1: xcur=xuh
		elif k==2: xcur=xdm
		elif k==3: xcur=xum
		self.draw.line([(xcur+1,ycur),(xcur+lpas-1,ycur)], fill = "RED",width = 5)
		
		self.disp.LCD_ShowImage(self.image,0,0)
	
	#activer ou non l'alarme beep
	def change_alarme_beep_status(self):
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["beepindex"]!=""): 
			self.DATA_INI["alarme"]["active"]="0"
			self.DATA_INI["alarme"]["radioindex"]=""
			self.DATA_INI["alarme"]["fileindex"]=""
		elif len(self.alarmelist)>0:
			self.DATA_INI["alarme"]["active"]="1"
			if (self.DATA_INI["alarme"]["beepindex"]==""): self.DATA_INI["alarme"]["beepindex"]="0"
			self.DATA_INI["alarme"]["radioindex"]=""
			self.DATA_INI["alarme"]["fileindex"]=""
		#va forcer le rafraichissement de l'écran
		self.oldmin=-1
		return
		
	#activer ou non l'alarme radio
	def change_alarme_radio_status(self):
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["radioindex"]!=""): 
			self.DATA_INI["alarme"]["active"]="0"
			self.DATA_INI["alarme"]["beepindex"]=""
			self.DATA_INI["alarme"]["fileindex"]=""
		elif len(self.radiolist)>0:
			self.DATA_INI["alarme"]["active"]="1"
			if (self.DATA_INI["alarme"]["radioindex"]==""): self.DATA_INI["alarme"]["radioindex"]="0"
			self.DATA_INI["alarme"]["beepindex"]=""
			self.DATA_INI["alarme"]["fileindex"]=""
		#va forcer le rafraichissement de l'écran
		self.oldmin=-1
		return
		
	#activer ou non l'alarme audio
	def change_alarme_audio_status(self):
		if (self.DATA_INI["alarme"]["active"]=="1") and (self.DATA_INI["alarme"]["fileindex"]!=""): 
			self.DATA_INI["alarme"]["active"]="0"
			self.DATA_INI["alarme"]["beepindex"]=""
			self.DATA_INI["alarme"]["radioindex"]=""
		elif len(self.audiolist)>0:
			self.DATA_INI["alarme"]["active"]="1"
			if (self.DATA_INI["alarme"]["fileindex"]==""): self.DATA_INI["alarme"]["fileindex"]="0"
			self.DATA_INI["alarme"]["beepindex"]=""
			self.DATA_INI["alarme"]["radioindex"]=""
		#va forcer le rafraichissement de l'écran
		self.oldmin=-1
		return
		
	#Alarme ON/OFF par l'écran principale
	def switch_alarme(self):
		if self.DATA_INI["alarme"]["active"]=="1": self.DATA_INI["alarme"]["active"]="0"
		elif self.DATA_INI["alarme"]["beepindex"]!="":
			self.DATA_INI["alarme"]["active"]="1"
			self.DATA_INI["alarme"]["radioindex"]=""
			self.DATA_INI["alarme"]["fileindex"]=""
		elif self.DATA_INI["alarme"]["radioindex"]!="":
			self.DATA_INI["alarme"]["active"]="1"
			self.DATA_INI["alarme"]["beepindex"]=""
			self.DATA_INI["alarme"]["fileindex"]=""
		elif self.DATA_INI["alarme"]["fileindex"]!="":
			self.DATA_INI["alarme"]["active"]="1"
			self.DATA_INI["alarme"]["beepindex"]=""
			self.DATA_INI["alarme"]["radioindex"]=""
	
	#changer station radio pour l'alarme ou l'écoute audio
	#en mode alarme : choisir une station active l'alarme sur la radion si pas de station : pas d'alarme
	def next_station(self,typ="alarme",liste=[]):
		if typ!="alarme" and typ!="audio": return
		s=self.DATA_INI[typ]["radioindex"]
		if s=="" and len(liste)>0: s="0"
		elif int(s)<len(liste)-1: s=str(int(s)+1)
		else: s=""
		self.DATA_INI[typ]["radioindex"]=s
		if (typ=="alarme") and (self.DATA_INI[typ]["radioindex"]!=""):
			self.DATA_INI[typ]["beepindex"]=""
			self.DATA_INI[typ]["fileindex"]=""
			self.DATA_INI[typ]["active"]="1"
		elif (typ=="alarme") and (self.DATA_INI[typ]["radioindex"]==""):
			self.DATA_INI[typ]["active"]="0"
		return
		
	#changer fichier audio pour l'alarme ou l'écoute audio
	def next_audiofile(self,typ="alarme",liste=[]):
		if typ!="alarme" and typ!="audio": return
		s=self.DATA_INI[typ]["fileindex"]
		if s=="" and len(liste)>0: s="0"
		elif int(s)<len(liste)-1: s=str(int(s)+1)
		else: s=""
		self.DATA_INI[typ]["fileindex"]=s
		if (typ=="alarme") and (self.DATA_INI[typ]["fileindex"]!=""):
			self.DATA_INI[typ]["beepindex"]=""
			self.DATA_INI[typ]["radioindex"]=""
			self.DATA_INI[typ]["active"]="1"
		elif (typ=="alarme") and (self.DATA_INI[typ]["fileindex"]==""):
			self.DATA_INI[typ]["active"]="0"
		return
		
	#changer beep pour l'alarme
	def next_beep(self,typ="alarme",liste=[]):
		if typ!="alarme" and typ!="audio": return
		s=self.DATA_INI[typ]["beepindex"]
		if s=="" and len(liste)>0: s="0"
		elif int(s)<len(liste)-1: s=str(int(s)+1)
		else: s=""
		self.DATA_INI[typ]["beepindex"]=s
		if (typ=="alarme") and (self.DATA_INI[typ]["beepindex"]!=""):
			self.DATA_INI[typ]["fileindex"]=""
			self.DATA_INI[typ]["radioindex"]=""
			self.DATA_INI[typ]["active"]="1"
		elif (typ=="alarme") and (self.DATA_INI[typ]["beepindex"]==""):
			self.DATA_INI[typ]["active"]="0"
		return
	
	#regler l'heure de l'alarme
	def change_heure_alarme(self,k,sens):
		if k<0: return
		if k>3: return
		if sens==0: return
		DH=int(self.DATA_INI["alarme"]["heure"][0])
		UH=int(self.DATA_INI["alarme"]["heure"][1])
		DM=int(self.DATA_INI["alarme"]["heure"][3])
		UM=int(self.DATA_INI["alarme"]["heure"][4])
		if k==0: DH=int(DH)+sens
		elif k==1: UH=UH+sens
		elif k==2: DM=DM+sens
		elif k==3: UM=UM+sens
		if DH<0: DH=2
		elif DH>2: DH=0
		if UH<0: UH=9
		elif UH>9: UH=0
		if DH*10+UH<0: 
			DH=2
			DU=3
		if DH*10+UH>23:
			DH=0
			DM=0
		if DM<0: DM=5
		elif DM>5: DM=0
		if UM<0: UM=9
		elif UM>9: UM=0
		if DM*10+UM>59:
			DM=0
			UM=0
		if DM*10+UM<0:
			DM=23
			UM=59
		self.DATA_INI["alarme"]["heure"]=str(DH)+str(UH)+":"+str(DM)+str(UM)

######################################
if (__name__ == "__main__"):
	
	
	#Pas d'horloge RTC présente
	RTC=False 
	if (RTC==True) : starting_rtc()
	
	print("DEMARRAGE A :")
	printcurrentdatetime()
	
	#########################################################
	# VERIFICATION INITIALES
	#########################################################
	if int(datetime.datetime.now().strftime("%Y"))<=2001:
		print("Date-Heure incorrecte : pas d'horloge et pas de connexion internet !")
		sys.exit(-1)
	
	reveil=MonReveil("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",False)
	
	if os.path.exists(reveil.audioplayerfilename)==False:
		print("Fichier "+reveil.audioplayerfilename+" absent")
		sys.exit(-1)
		
	if os.path.exists(reveil.alarmelistfilename)==False:
		print("Fichier "+reveil.alarmelistfilename+" absent")
		sys.exit(-1)

	if len(reveil.alarmelist)==0:
		print("Le fichier "+reveil.alarmelistfilename+" ne contient pas d'information concernant un fichier de beep à utiliser comme alarme")
		sys.exit(-1)
		
	#########################################################
	# FIN DES VERIFICATIONS INITIALES
	#########################################################
	#Clavier
	reveil.KB.start()
	#Preparer une page vierge
	reveil.prepare_page_vierge()
	#Boucle infinie
	
	while True:
		try:
			#Arrêt auto du réveil si lancé
			reveil.autostop_alarme()
			#PAGE NORMALE
			if (reveil.page==0):
				k=0
				reveil.ecran_heure()
				reveil.KB.lock.acquire()
				btn,typ=reveil.KB.wich_btn()
				#play / pause
				if (btn=="K_1") and (typ=="long"):
					s=reveil.DATA_INI["audio"]["beepindex"]
					if s=="": s="-1"
					if int(s)>=0 and int(s)<len(reveil.alarmelist): 
						reveil.oldmin=-1
						reveil.start_stop_playing_audio(reveil.alarmelist[int(s)]["filename"])
				elif (btn=="K_2") and (typ=="long"):
					s=reveil.DATA_INI["audio"]["radioindex"]
					if s=="": s="-1"
					if int(s)>=0 and int(s)<len(reveil.radiolist): 
						reveil.oldmin=-1
						reveil.start_stop_playing_audio(reveil.radiolist[int(s)]["url"])
				elif (btn=="K_3") and (typ=="long"):
					s=reveil.DATA_INI["audio"]["fileindex"]
					if s=="": s="-1"
					if int(s)>=0 and int(s)<len(reveil.audiolist): 
						reveil.oldmin=-1
						reveil.start_stop_playing_audio(reveil.audiolist[int(s)]["filename"])
				#activer alarme / désactiver alarme
				elif (btn=="K_PRESS") and (typ=="long"):
					reveil.switch_alarme()
					reveil.oldmin=-1
				#entrer dans écran réglage alarme
				elif (btn=="K_UP") and (typ=="long"):
					reveil.page=1
				#switch entre les sélections beep - radio - audio
				elif (btn=="K_1") and (typ=="short"):
					if reveil.radiothread!=None: reveil.start_stop_playing_audio("")
					reveil.next_beep("audio",reveil.alarmelist)
					reveil.oldmin=-1
				elif (btn=="K_2") and (typ=="short"):
					if reveil.radiothread!=None: reveil.start_stop_playing_audio("")
					reveil.next_station("audio",reveil.radiolist)
					reveil.oldmin=-1
				elif (btn=="K_3") and (typ=="short"):
					if reveil.radiothread!=None: reveil.start_stop_playing_audio("")
					reveil.next_audiofile("audio",reveil.audiolist)
					reveil.oldmin=-1
				#arrêter le reveil ou toute sortie sonore
				elif (btn=="K_PRESS") and (typ=="short"):
					if reveil.radiothread!=None: reveil.start_stop_playing_audio("")
				reveil.KB.lock.release()
				time.sleep(0.01)
			#PAGE REGLAGE ALARME
			if (reveil.page==1):
				reveil.ecran_alarme(k)
				reveil.KB.lock.acquire()
				btn,typ=reveil.KB.wich_btn()
				#Sortie
				if (btn=="K_UP") and (typ=="long"):
					saveini(reveil.DATA_INI,reveil.ficini)
					reveil.page=0
					reveil.oldmin=-1
				#déplacement curseur heure de réveil
				elif (btn=="K_PRESS") and (typ=="short"):
					k=k+1
					if (k>3): k=0
					if (k<0): k=3
				#changer heure de l'alarme
				elif (btn=="K_LEFT") and (typ=="short"):reveil.change_heure_alarme(k,-1)
				elif (btn=="K_RIGHT") and (typ=="short"): reveil.change_heure_alarme(k,+1)
				#switch entre beep et agtivation on/off
				elif (btn=="K_1") and (typ=="short"):
					reveil.next_beep("alarme",reveil.alarmelist)
				#switch entre stations de radio pour l'alarme et activation on/off
				elif (btn=="K_2") and (typ=="short"):
					reveil.next_station("alarme",reveil.radiolist)
				#switch entre fichier mp3 pour l'alarme et activation on/off
				elif (btn=="K_3") and (typ=="short"):
					reveil.next_audiofile("alarme",reveil.audiolist)
				reveil.refreshalarme=(btn!=None)
				reveil.KB.lock.release()
				time.sleep(0.01)
		except KeyboardInterrupt:
			#reveil.KB.join()
			#stopper une lecture de son si en cours
			reveil.start_stop_playing_audio("")
			sys.exit(-1)

