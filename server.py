#!/usr/bin/python3
# pip3 install requests
# pip3 install http
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import sys
import os
import json
import urllib.parse
from tools import *

COLOR = "\033[1;32m"
RESET_COLOR = "\033[00m"
DEFAULTPORT=9000

def formdata_to_data(formdata):
	data={}
	data["alarme"]={"heure":formdata["alarme_heure"]+":"+formdata["alarme_minute"],"duree":formdata["alarme_duree"],"active":formdata["alarme_active"],"beepindex":"","radioindex":"","fileindex":""}
	if formdata["alarme_type"].lower()=="beep": data["alarme"]["beepindex"]=formdata["alarme_playbeep"]
	elif formdata["alarme_type"].lower()=="radio": data["alarme"]["radioindex"]=formdata["alarme_playradio"]
	elif formdata["alarme_type"].lower()=="fichier": data["alarme"]["fileindex"]=formdata["alarme_playaudio"]
	data["click"]={"long":formdata["click_long"],"short":formdata["click_short"]}
	data["color"]={"background":formdata["color_background"],"font_1_d":formdata["color_font_1_d"],"font_2_d":formdata["color_font_2_d"],"font_1_n":formdata["color_font_1_n"],"font_2_n":formdata["color_font_2_n"],"ico_d":formdata["color_ico_d"],"ico_n":formdata["color_ico_n"],"day_start":formdata["color_day_start_heure"]+":"+formdata["color_day_start_minute"],"day_end":formdata["color_day_end_heure"]+":"+formdata["color_day_end_minute"]}
	data["audio"]={"beepindex":formdata["audio_beepindex"],"fileindex":formdata["audio_fileindex"],"radioindex":formdata["audio_radioindex"]}
	return data


def loadtbcolor():
	result=[]
	for i in range(0,16):
		a=hex(16*i).replace("0x","")
		if len(a)==1: a="0"+a
		for j in range(0,16):
			b=hex(16*j).replace("0x","")
			if len(b)==1: b="0"+b
			for k in range(0,16):
				c=hex(16*k).replace("0x","")
				if len(c)==1: c="0"+c
				result.append("#"+(c+b+a).upper())
	return result
	

def mkform(data,audiolist,radiolist,beeplist):
	s=""
	s+="<div class='contenumobile'>"
	s+="<form method=POST>"
	#######################################################
	##  ALARME 
	#######################################################
	s+="<div class='data_profil'><h1>Alarme</h1>"
	s+="<table style='border:none; border-spacing:0px 5px;'>"
	s+="<tbody>"
	s+="<tr class='data_profil'>"
	s+="<td>Heure</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_heure'>"
	for i in range(0,24):
		s+="<option value='"+"{:02d}".format(i)+"' "
		if (int(data["alarme"]["heure"][0:2])==i): s+=" selected "
		s+=">"+"{:02d}".format(i)+"</option>"
	s+="</select>"
	s+=" : "
	s+="<select name='alarme_minute'>"
	for i in range(0,60):
		s+="<option value='"+"{:02d}".format(i)+"' "
		if (int(data["alarme"]["heure"][3:5])==i): s+=" selected "
		s+=">"+"{:02d}".format(i)+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	s+="<tr class='data_profil'>"
	s+="<td>Active</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_active'>"
	s+="<option value='0' "
	if (int(data["alarme"]["active"])==0): s+=" selected "
	s+=">Non</option>"
	s+="<option value='1' "
	if (int(data["alarme"]["active"])==1): s+=" selected "
	s+=">Oui</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	s+="<tr class='data_profil'>"
	s+="<td >Durée</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_duree'>"
	for i in range(1,13):
		s+="<option value='"+"{:02d}".format(5*i)+"' "
		if (int(data["alarme"]["duree"])==i*5): s+=" selected "
		s+=">"+"{:02d}".format(i*5)+" minutes</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	s+="<tr class='data_profil'>"
	s+="<td>Type</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_type' id='alarme_type' onchange='change_alarm_type(this.id);' >"
	s+="<option value='Beep' "
	if (data["alarme"]["beepindex"]!=""): s+=" selected "
	s+=">Beep</option>"
	s+="<option value='Fichier' "
	if (data["alarme"]["fileindex"]!=""): s+=" selected "
	s+=">Audio</option>"
	s+="<option value='Radio' "
	if (data["alarme"]["radioindex"]!=""): s+=" selected "
	s+=">Radio</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	s+="<tr class='data_profil' id='play_audio'>"
	s+="<td>Play</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_playaudio' id='alarme_playaudio' >"
	s+="<option value='' " 
	if (data["alarme"]["fileindex"]==""): s+=" selected ></option>"
	for i in range(0,len(audiolist)):
		s+="<option value='"+str(i)+"' "
		if (str(data["alarme"]["fileindex"])==str(i)): s+=" selected "
		s+=">"+audiolist[i]['name']+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	s+="<tr class='data_profil' id='play_beep'>"
	s+="<td>Play</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_playbeep' id='alarme_playbeep' >"
	s+="<option value='' " 
	if (data["alarme"]["beepindex"]==""): s+=" selected ></option>"
	for i in range(0,len(beeplist)):
		s+="<option value='"+str(i)+"' "
		if (str(data["alarme"]["beepindex"])==str(i)): s+=" selected "
		s+=">"+beeplist[i]['name']+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	s+="<tr class='data_profil' id='play_radio'>"
	s+="<td>Play</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='alarme_playradio'>"
	s+="<option value='' " 
	if (data["alarme"]["radioindex"]==""): s+=" selected ></option>"
	for i in range(0,len(radiolist)):
		s+="<option value='"+str(i)+"' "
		if (str(data["alarme"]["radioindex"])==str(i)): s+=" selected "
		s+=">"+radiolist[i]['name']+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"

	s+="</tbody></table>"
	s+="</div>"
	#######################################################
	##  LECTURE AUDIO LIVE 
	#######################################################
	s+="<br>"
	s+="<div class='data_profil'><h1>Audio Live</h1>"
	s+="<table style='border:none; border-spacing:0px 5px;'>"
	s+="<tbody>"
	s+="<tr class='data_profil'>"
	s+="<td>Play Beep</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='audio_beepindex'>"
	s+="<option value='' " 
	if (data["audio"]["beepindex"]==""): s+=" selected ></option>"
	for i in range(0,len(beeplist)):
		s+="<option value='"+str(i)+"' "
		if (str(data["audio"]["beepindex"])==str(i)): s+=" selected "
		s+=">"+beeplist[i]['name']+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Play Audio</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='audio_fileindex'>"
	s+="<option value='' " 
	if (data["audio"]["fileindex"]==""): s+=" selected ></option>"
	for i in range(0,len(audiolist)):
		s+="<option value='"+str(i)+"' "
		if (str(data["audio"]["fileindex"])==str(i)): s+=" selected "
		s+=">"+audiolist[i]['name']+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Play Radio</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='audio_radioindex'>"
	s+="<option value='' " 
	if (data["audio"]["radioindex"]==""): s+=" selected ></option>"
	for i in range(0,len(radiolist)):
		s+="<option value='"+str(i)+"' "
		if (str(data["audio"]["radioindex"])==str(i)): s+=" selected "
		s+=">"+radiolist[i]['name']+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"

	s+="</td>"
	s+="</tr>"
	s+="</tbody></table>"
	s+="</div>"
	
		
	#######################################################
	##  CLICS 
	#######################################################
	s+="<br>"
	s+="<div class='data_profil'><h1>Durée des clics</h1>"
	s+="<table style='border:none; border-spacing:0px 5px;'>"
	s+="<tbody>"
	s+="<tr class='data_profil'>"
	s+="<td>Clic long (ms)</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='click_long'>"
	for i in range(1,21):
		s+="<option value='"+str(i*50)+"' "
		if (int(data["click"]["long"])==i*50): s+=" selected "
		s+=">"+str(50*i)+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Clic court (ms)</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='click_short'>"
	for i in range(1,31):
		s+="<option value='"+str(i*10)+"' "
		if (int(data["click"]["short"])==i*10): s+=" selected "
		s+=">"+str(10*i)+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="</tbody>"
	s+="</table>"
	s+="</div>"
	
	#######################################################
	##  COLORS 
	#######################################################
	s+="<br>"
	s+="<div class='data_profil'><h1>Couleurs</h1>"
	s+="<table style='border:none; border-spacing:0px 5px;'>"
	s+="<tbody>"
	
	s+="<tr class='data_profil'>"
	s+="<td>Début du jour à</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='color_day_start_heure'>"
	for i in range(0,24):
		s+="<option value='"+"{:02d}".format(i)+"' "
		if (int(data["color"]["day_start"][0:2])==i): s+=" selected "
		s+=">"+"{:02d}".format(i)+"</option>"
	s+="</select>"
	s+=" : "
	s+="<select name='color_day_start_minute'>"
	for i in range(0,12):
		s+="<option value='"+"{:02d}".format(5*i)+"' "
		if (int(data["color"]["day_start"][3:5])==5*i): s+=" selected "
		s+=">"+"{:02d}".format(5*i)+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Début de nuit à</td>"
	s+="<td nowrap style='min-width:120px;'>"
	s+="<select name='color_day_end_heure'>"
	for i in range(0,24):
		s+="<option value='"+"{:02d}".format(i)+"' "
		if (int(data["color"]["day_end"][0:2])==i): s+=" selected "
		s+=">"+"{:02d}".format(i)+"</option>"
	s+="</select>"
	s+=" : "
	s+="<select name='color_day_end_minute'>"
	for i in range(0,12):
		s+="<option value='"+"{:02d}".format(5*i)+"' "
		if (int(data["color"]["day_end"][3:5])==5*i): s+=" selected "
		s+=">"+"{:02d}".format(5*i)+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	
	
	s+="<tr class='data_profil'>"
	s+="<td>Couleur de fond</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["background"]+";'>"
	s+="<select name='color_background' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["background"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Font de jour 1</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["font_1_d"]+";'>"
	s+="<select name='color_font_1_d' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["font_1_d"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"

	s+="<tr class='data_profil'>"
	s+="<td>Font de jour 2</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["font_2_d"]+";'>"
	s+="<select name='color_font_2_d' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["font_2_d"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Font de nuit 1</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["font_1_n"]+";'>"
	s+="<select name='color_font_1_n' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["font_1_n"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Font de nuit 2</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["font_2_n"]+";'>"
	s+="<select name='color_font_2_n' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["font_2_n"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Icone de jour</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["ico_d"]+";'>"
	s+="<select name='color_ico_d' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["ico_d"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
	s+="<tr class='data_profil'>"
	s+="<td>Icone de nuit</td>"
	s+="<td nowrap style='min-width:120px;  background-color:"+data["color"]["ico_n"]+";'>"
	s+="<select name='color_ico_n' onchange=\"this.parentNode.style.backgroundColor = this.value\">"
	for i in range(0,len(TBCOLOR)):
		s+="<option value='"+TBCOLOR[i]+"' style='background-color: "+TBCOLOR[i]+";'"
		if (data["color"]["ico_n"]==TBCOLOR[i]): s+=" selected "
		s+=">"+TBCOLOR[i]+"</option>"
	s+="</select>"
	s+="</td>"
	s+="</tr>"
		
	s+="</tbody>"
	s+="</table>"
	s+="</div>"
	
	s+="<br>"
	s+="<div class='data_profil'>"
	s+="<input class='mobile_button' type=submit name='OK'></td></tr>"
	s+="</div>"
	
	s+="</form>"


	s+="<script>change_alarm_type('alarme_type')</script>";
	return s

class PageWeb():
	def __init__(self,title=""):
		with open(BASETEMPLATE) as html_template:
			self.html=html_template.read().rstrip()
	
	def set_title(self,title=""):
		self.html=self.html.replace("{@title}",title)
	
	def set_headers(self,headers):
		shead="\r\n".join(headers)
		self.html=self.html.replace("{@headers}",shead)

	def set_body(self,body=""):
		self.html=self.html.replace("{@body}",body)
		
	def set_style(self,stylefilename):
		with open(stylefilename) as f:
			style=f.read().rstrip()
		self.html=self.html.replace("{@style}",style)


class S(BaseHTTPRequestHandler):
	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		
	def do_log(self, method):
		content_length = self.headers['Content-Length']
		content_length = 0 if (content_length is None) else int(content_length)
		post_data = self.rfile.read(content_length)
		logging.info(COLOR + method + " request,\n" + RESET_COLOR + "Path: %s\nHeaders:\n%sBody:\n%s\n",
				str(self.path), str(self.headers), post_data.decode('utf-8'))
		self._set_response()
		if (method == "POST"):
			s=urllib.parse.unquote(post_data.decode('utf-8'))
			#print("----------------------")
			#print("post_data=")
			#print(post_data)
			#print(type(post_data))
			#print("s=")
			#print(s)
			#print(type(s))

			tb=s.split("&")
			#print("tb=")
			#print(type(tb))
			#print(str(tb))
			print("----------------------")
			self.post_data={}
			for i in range(0,len(tb)):
				a=tb[i].split("=")
				self.post_data[a[0]]=a[1]
		#self.wfile.write((method + " request for {}".format(self.path)).encode('utf-8'))

	def do_GET(self):
		self.do_log("GET")
		RADIOLIST=loadjson(RADIOLISTFILE)
		ALARMELIST=loadjson(ALARMELISTFILE)
		AUDIOLIST=loadjson(AUDIOLISTFILE)
		self.DATA=loadini(PARAMFILE,ALARMELIST,RADIOLIST,AUDIOLIST)
		#print(self.DATA)
		
		pageweb=PageWeb()
		pageweb.set_title("PiReveil")
		head=[]
		with open(JSFILE) as js:
			jsdata="<script>"+js.read().rstrip()+"</script>"
		head.append(jsdata)
		pageweb.set_headers(head)
		pageweb.set_style(CSSFILE)
		pageweb.set_body(mkform(self.DATA,AUDIOLIST,RADIOLIST,ALARMELIST))
		self.wfile.write(pageweb.html.encode('utf-8'))
		
	def do_POST(self):
		self.do_log("POST")
		#print("---  post_data")
		#print(self.post_data)
		self.DATA=formdata_to_data(self.post_data)
		#print(self.DATA)
		saveini(self.DATA,PARAMFILE)
		
		self.send_response(301)
#		self.send_header('Content-type', 'text/html')
#		self.end_headers()
		RADIOLIST=loadjson(RADIOLISTFILE)
		ALARMELIST=loadjson(ALARMELISTFILE)
		AUDIOLIST=loadjson(AUDIOLISTFILE)
		self.DATA=loadini(PARAMFILE,ALARMELIST,RADIOLIST,AUDIOLIST)
		#print(self.DATA)
		
		pageweb=PageWeb()
		pageweb.set_title("PiReveil")
		head=[]
		with open(JSFILE) as js:
			jsdata="<script>"+js.read().rstrip()+"</script>"
		head.append(jsdata)
		pageweb.set_headers(head)
		pageweb.set_style(CSSFILE)
		pageweb.set_body(mkform(self.DATA,AUDIOLIST,RADIOLIST,ALARMELIST))
		self.wfile.write(pageweb.html.encode('utf-8'))


	def do_PUT(self):
		self.do_log("PUT")

	def do_DELETE(self):
		self.do_log("DELETE")

def run(address='',port=DEFAULTPORT,server_class=HTTPServer, handler_class=S):
	logging.basicConfig(level=logging.INFO)
	server_address = (address, port)
	httpd = server_class(server_address, handler_class)
	logging.info('Starting httpd...on port %d...addresse %s\n',port,address)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	logging.info('Stopping httpd...\n')

if __name__ == '__main__':
	ad='0.0.0.0'
	PORT=DEFAULTPORT
	print("Usage:\n" + sys.argv[0] + " [address] [port]")
	if len(sys.argv) >= 2: ad=sys.argv[1]
	if len(sys.argv) >= 3: PORT=sys.argv[2]
	
	rootdir=os.path.dirname(os.path.realpath(__file__))
	if not rootdir.endswith(os.path.sep): rootdir += os.path.sep
	RADIOLISTFILE=rootdir+"radiolist.json"
	ALARMELISTFILE=rootdir+"alarmelist.json"
	AUDIOLISTFILE=rootdir+"audiolist.json"
	BASETEMPLATE=rootdir+"base.html"
	CSSFILE=rootdir+"style.css"
	JSFILE=rootdir+"tools.js"
	PARAMFILE=rootdir+"param.ini"
	TBCOLOR=loadtbcolor()
	
	run(ad,PORT)
