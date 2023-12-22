#! /bin/bash
if [ ! -f /home/pi/pireveil/pireveil.service ]; then
   echo "Fichier /home/pi/pireveil/pireveil.service  absent"
   exit 99
fi   
sudo cp /home/pi/pireveil/pireveil.service  /lib/systemd/system/pireveil.service
r=$?
if [ $r -ne 0 ]; then
   echo "Une erreur s'est produite"
   exit 1
fi
sudo systemctl daemon-reload
sudo systemctl enable pireveil.service