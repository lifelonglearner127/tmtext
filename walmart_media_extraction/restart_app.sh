dir="/home/ubuntu/tmtext/walmart_media_extraction"
mkdir -p "$dir"/logs
/usr/bin/pkill -f walmart_media_app;
/usr/bin/screen -dm /bin/bash "$dir"/start_app.sh 2>>"$dir"/logs/startapp_log.txt
