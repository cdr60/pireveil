#!/usr/bin/python3
#pip3 install playsound
##apt install libgstreamer1.0 libgstreamer1.0-dev gstreamer1.0-tools
####################################################################
## LECTURE URL OU M3U OU FICHIER AUDIO A STREAMER
## UTILISATION : CHEMIN COMPLET (OU RUL) EN ARGUMENT
####################################################################
from playsound import playsound
import os
import sys

def is_url(string):
	return  ((string.lower()[0:7]=="http://") or (string.lower()[0:8]=="https://"))

def is_m3u(string):
	if is_url(string): return False
	if os.path.isfile(string)==False: return False
	tb=string.split(".")
	if len(tb)==0: return False
	return (tb[len(tb)-1].lower()=="m3u")
		

def is_audiofile(string):
	if is_url(string): return False
	if is_m3u(string): return False
	if os.path.isfile(string)==False: return False
	return True
	

def play_my_m3u(filename):
	m3udir = os.path.dirname(filename)
	if m3udir!="":
		if m3udir[len(m3udir)-1:len(m3udir)]!="/": m3udir+="/"
	mu3lines=[]
	f=open(filename,"r")
	while True:
		l=f.readline()
		if not l: break
		fname=""
		fname=l.strip()
		if os.path.isfile(m3udir+fname): mu3lines.append(m3udir+fname)
	f.close()
	for i in range(0,len(mu3lines)-1):
		playsound(mu3lines[i])
	return


arg=sys.argv[1:]
if len(arg)==0: 
	print("Argument manquant")
	print("Argument autorisé : chemin complet de fichier m3u ou mp3 ou wav ou une url de streaming")
	sys.exit(-1)

if is_m3u(arg[0]):
	print("Lecture m3u")
	play_my_m3u(arg[0])
elif is_url(arg[0]):
	print("Lecture url")
	playsound(arg[0])
elif is_audiofile(arg[0]):
	print("Lecture audio")
	playsound(arg[0])
sys.exit(0)	
