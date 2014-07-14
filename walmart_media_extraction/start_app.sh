dir="/home/ubuntu/tmtext/walmart_media_extraction"
mkdir -p "$dir"/logs
time=`date +"%F"`
python "$dir"/walmart_media_app.py 2>>"$dir"/logs/log_"$time".txt
