# Pi Dream Machine (pireveil)
Raspberry Pi Dream machine : French version on my blog at <a href='https://blog-info.cd-ii.fr/un-radio-reveil-a-base-de-raspiberry-pi/'>https://blog-info.cd-ii.fr/un-radio-reveil-a-base-de-raspiberry-pi/</a>
<br><br>

Building a dream machine using a Raspberry Pi

<img src="./images/pireveil.png" width="256"/>
<br><br>

# What do you need ?
<ul>
<li>A raspberry Pi (whichever you choose : Pi Zero, 1, 2, 3, 4 ,5) with an internet connexion (Ethernet or Wifi)<br>
Mine is a Raspberry Pi2 with a Wifi USB dongle and a silent cooling box like this<br><br>
<img src="./images/radiateur_pi.png" width="256"/>
</li>
<li>An Oled screen 128x128 pixels with 3 buttons and 1 joypad (from Waveshare)<br><br>
<img src="./images/1.44inch-lcd-hat-1.jpg" width="256"/>
</li>
<li>Raspberry OS Lite (no need for Desktop) 
</li>
<li>External speakers</li>
</ul>

# What do you have to know before ?
<ul>
<li>How to begin with a Rapsberry Pi (using a SD Card, installing the OS)</li>
<li>How to launch commands via Terminal or ssh client</li>
</ul>

# What these dream machine can do  ?
<ul>
<li>Shows current date and time</li>
<li>Lets you set an alarm</li>
<li>Lets you choose what the Pi will play to wake you up</li>
<li>Lets you choose between some sound samples, mp3, m3u, web radio to listen now or to be used to wake you up</li>
<li>Automatic font color change (day/night) to reduce brightness</li>
</ul>

# What technologies does it use  ?
<ul>
<li>Python 3</li>
<li>Systemctl service setting</li>
<li>Internet web radio streaming</li>
</ul>

# What will you find on the repository  ?
<ul>
<li>Alarme directory : some mp3 files you can use to wake you up
    <ul>
    <li>beep.mp3 : a simple beep sound</li>
    <li>incendie.mp3 : a fire alarm sound</li>
    <li>coq.mp3 : a rooster crowing sound</li>
    </ul>
</li> 
<li>Musique directory
    <ul>
    <li>You have to put your favorites mp3 songs here</li>
    </ul>
</li>   
<li>root directory
    <ul>
    <li>alarmelist.json : a json file that describes which alarm sounds you can choose (mp3 files must exist in alarme directory)</li>
    <li>audio.json : a json file that describes which mp3 or m3u files you can choose (mp3 and m3u files must exist in musique directory).<br>
    I put my personnal audio list here but can't include it due to copyright reasons</li>
    <li>create_m3u.sh : a simple shell script that helps you create your own m3u files</li>
    <li>installpackage.sh : a simple shell script that will install all packages and libraries you need</li>
    <li>installsertvice.sh : a simple shell script that will install the service to make PiReveil start each time the Pi is rebooted.<br><b>Be careful</b> : it assumes that everything is in /home/pi/pireveil/. If not, you will have to change it</li>
    <li>key_demo.py : a short script included with the screen when you bought it that helps you test the screen and the buttons</li>
    <li>LCD_1in44.py and LCD_Config.py : Essential libraries to control the screen</li>
    <li>main.py : a short script included with the screen when you bought it that demonstrates the screen's capabilities</li>
    <li>param.ini : Dream machine parameters</li>
    <li>pireveil.py : the PiReveil software</li>
    <li>pireveil.service : the PiReveil description service file for systemctl <b>Be careful</b> Open it and change the directories path in the script if necessary</li>
    <li>play.py : A very simple python script used by pireveil.py to play mp3 or m3u files and radio streaming</li>
    <li>radiolist.json : a json file that describes and list some webradios (make your own with your favorite editor)</li>
    <li>time.bmp : An image that pireveil will show while starting</li>
    </ul>
</li> 
</ul>

# param.ini description :
Opening this text file you will see variables and values
<ul>
<li>alarme section: Here, pireveil.py will load and save your parameters (alarm clock, what to do to wake you up)</li>
<li>audio section: what file will be played if you ask to listen it. index values corresponds to json files</li>
<li>click section: short : the minimum click time to understand that it is a short click. Long : same for long click (in ms)</li>
<li>color section: d is for day, n is for night. font_1 is for big font text. font_2 is for small font text. ico is for icons</li>
</ul>   

Using buttons, pireveil.py will change and save alarme and audio sections
If you want to change click or color settins, you will have to open param.ini and change theres values.

# How to install
<ul>
<li>Launch sudo bash installpackage.sh</li>
<li>Check your screen and your buttons with python3 main.py and python3 key_demo.py</li>
<li>Launch pireveil.py to check it works</li>
<li>Put some mp3 files in musique folder and change audiolist.json content</li>
<li>Launch again pireveil.py to check it works</li>
<li>Open installservice.sh and pireveil.service to use the folder you have installed pireveil</li>
<li>Launch sudo bash installservice.sh</li>
<li>Launch sudo systemctl start pireveil.service</li>
<li>Launch sudo systemctl status pireveil.service. If it's ok ? Well it's done !</li>
</ul> 

# How to use : the screens
<b>PiReveil can show 2 differents screens</b>
The first is the main. It shows :
<ul>
<li>
If playing someting : a play icons
</li>
<li>
3 icons : for beeping, listening radio and listening mp3 or m3u. If one is red then alarm is on and the red one describes what pireveil will do
</li>
<li>
Current time
</li>
<li>
Current date
</li>
<li>
Current alarm time and what pireveil will do (radio stations name , mp3 name or beep file name)
</li>
<li>
If set, what you can listen now (radio stations name , mp3 name or beep file name)
</li>
</ul>

<b>The second is the alarmclock seetings. It shows :</b>
<ul>
<li>
If playing someting : a play icons
</li>
<li>
3 icons : for beeping, listening radio and listening mp3 or m3u. If one is red then alarm is on and the red one describes what pireveil will do
</li>
<li>
Current alarm time and a red cursor that indicates what digit you can change now
</li>
</ul>

# How to use : the buttons
<b>On the main screen :</b>
<ul>
<li>K1 short click : select next beep sound to listen until none and then select first</li>
<li>K2 short click : select next radio station  to listen until none and then select first</li>
<li>K3 short click : select next mp3/mu3 fiels  to listen until none and then select first</li>
<li>K1 long click : start/stop listening selected beep file</li>
<li>K2 long click : start/stop listening selected radio station</li>
<li>K3 long click : start/stop listening selected mp3 or mu3 file</li>
<li>Joypad short keypress : stop listening whatever the source is (Ex : it stops alarm as well as listening radio)</li>
<li>Joypad long keypress : Arming alarm with audio source selected</li>
<li>Joypad long UP : Go to alarm screen</li>
</ul>

<b>On the alarm screen :</b>
<ul>
<li>K1 short click : select next beep sound to play on alarm event until none and then select first</li>
<li>K2 short click : select next radio station to play on alarm event until none and then select first</li>
<li>K3 short click : select next mp3/mu3 files to play on alarm event until none and then select first</li>
<li>Joypad short keypress : Select alarm clock next digit</li>
<li>Joypad short left : decrease selected digit</li>
<li>Joypad short right : increase selected digit</li>
<li>Joypad long UP : Return to main screen</li>
</ul>

