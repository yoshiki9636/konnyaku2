cd /home/pi/konnyaku2
export GOOGLE_APPLICATION_CREDENTIALS='<Json file path>'
export GOOGLE_CLOUD_PROJECT='<Project name>'
python3 konnyaku2.py 1> /dev/null 2>&1
#python3 konnyaku2.py 1> /home/pi/log.txt 2>&1

