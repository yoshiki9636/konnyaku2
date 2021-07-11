import pyaudio
import time
import wave
import numpy
import speech_recognition as sr
from google.cloud import translate
from os import path
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# settings
FRAMES_PER_BUFFER = 4096
CHANNELS = 1 # Monaral
SAMPLEWIDTH = 2 # 16bit width
RATE = 16000

# Device setting
DEVICE_INDEX = 0
 
# call back function for wave recordign
def callback(in_data, frame_count, time_info, status):
    wf.writeframes(in_data)
    return (None, pyaudio.paContinue)

# recognization with calling Google 
def recognizing(name, from_target, to_target):
    # Instantiates a client
    translate_client = translate.Client()
    r = sr.Recognizer()
    with sr.AudioFile(name) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Google Speech Recognition
    try:
        # STT using google
        text = r.recognize_google(audio, language=from_target)
        f.write(text + "\n")
        print("Google Speech Recognition thinks you said " + text)
        # google translation
        translation = translate_client.translate(text, target_language=to_target)
        text2 = translation['translatedText']
        print(text2)
        # making words file
        f.write(text2 + "\n")
        # TTS using espeak for English, jsay for Japanese
        if to_target == 'en':
            spc = ["espeak","-ven+f3","-k5","-s150"]
        else:
            spc = ["./jsay.sh"]
        text3 = "\""+text2+"\""
        spc.append(text3)
        subprocess.call(spc)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return

def start_wave_stream(cntr):
    # wave file setting
    name = "./sound/sound" + str(cntr) + ".wav"
    wf = wave.open(name,'w')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPLEWIDTH)
    wf.setframerate(RATE)
    # starts pyaudio
    p = pyaudio.PyAudio()
    # starts stream
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    input_device_index = DEVICE_INDEX,
                    input = True,
                    output = False,
                    frames_per_buffer = FRAMES_PER_BUFFER,
                    stream_callback = callback)
    return wf, p, stream

def finish_wave_stream(wf,p,stream,name,from_terget,to_target):
    # stop stream
    stream.stop_stream()
    stream.close()
    # close wavefile
    wf.close()
    # finish pyaudio
    p.terminate()
    # recognize, translate and speech
    recognizing(name, from_target, to_target)  
    return

def main():
    # setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) # ja->en
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # en->ja

    f = open('output.txt', mode='w')
    cntr = 0
    pushflg_ja = False
    pushflg_en = False
    from_target = 'en'
    to_target = 'ja'
    try:
       lp = True
        while lp:
            # Check ja->en
            if GPIO.input(23) == GPIO.LOW:
                if not pushflg_en:
                    from_target = 'ja'
                    to_target = 'en'
                #else:
                    #continue
                # start recording Japanese wavefile
                if not pushflg_ja:
                    pushflg_ja = True
                    cntr = cntr + 1
                    wf, p, stream = start_wave_stream(cntr)
                    print('>>> recording japanese now...  ')
            else:
                # stop recording Japanese wavefile
                if pushflg_ja:
                    pushflg_ja = False
                    finish_wave_stream(wf,p,stream,name,from_terget,to_target)
    
            # Check en->ja
            if GPIO.input(24) == GPIO.LOW:
                if not pushflg_ja:
                    from_target = 'en'
                    to_target = 'ja'
                #else:
                    #continue
                # start recording English wavefile
                if not pushflg_en:
                    pushflg_en = True
                    cntr = cntr + 1
                    wf, p, stream = start_wave_stream(cntr)
                    print('>>> recording english now...  ')
            else:
                # stop recording English wavefile
                if pushflg_en:
                    pushflg_en = False
                    finish_wave_stream(wf,p,stream,name,from_terget,to_target)
            # wait
            sleep(0.5)
     
    except KeyboardInterrupt:
        pass
    f.close()

if __name__ == '__main__':
    main()
