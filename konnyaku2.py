import io
import pyaudio
import time
import wave
import numpy
#import speech_recognition as sr
from google.cloud import translate_v2 as translate
from google.cloud import speech
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
DEVICE_INDEX = 1
 
# recognization with calling Google 
def recognizing(name, from_target, to_target):
    # Instantiates a client
    speech_client = speech.SpeechClient()
    translate_client = translate.Client()
    #r = sr.Recognizer()
    with io.open(name, "rb") as source:
        content = source.read()
    audio = speech.RecognitionAudio(content=content) 
    lang_code = "en-US" if from_target == 'en' else "ja-JP"
    config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=lang_code)
    try:
        # STT using google
        response = speech_client.recognize(config=config, audio=audio)
        text = ''
        for result in response.results:
            text += result.alternatives[0].transcript
        #text = r.recognize_google(audio, language=from_target)
        print("Google Speech Recognition thinks you said " + text)
        # google translation
        translation = translate_client.translate(text, target_language=to_target)
        text2 = translation['translatedText']
        print(text2)
        # making words file
        # TTS using espeak for English, jsay for Japanese
        if to_target == 'en':
            spc = ["espeak","-ven+f3","-k5","-s150"]
        else:
            spc = ["./jsay.sh"]
        text3 = "\""+text2+"\""
        spc.append(text3)
        subprocess.call(spc)
    except:
        print("Google Speech Recognition could not understand audio")
    return

def start_wave_stream(cntr,wf):
    # call back function for wave recordign
    def callback(in_data, frame_count, time_info, status):
        wf.writeframes(in_data)
        return (None, pyaudio.paContinue)

    # wave file setting
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPLEWIDTH)
    wf.setframerate(RATE)
    # starts pyaudio
    p = pyaudio.PyAudio()
    # starts stream
    """
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    input_device_index = DEVICE_INDEX,
                    input = True,
                    output = False,
                    frames_per_buffer = FRAMES_PER_BUFFER,
                    stream_callback = callback)
    """
    stream = p.open(format = pyaudio.paInt16,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    input_device_index = DEVICE_INDEX,
                    frames_per_buffer = FRAMES_PER_BUFFER,
                    stream_callback = callback)
    return wf, p, stream

def finish_wave_stream(wf,p,stream,name,from_target,to_target):
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
                    name = "./sound/sound" + str(cntr) + ".wav"
                    wf = wave.open(name,'w')
                    wf, p, stream = start_wave_stream(cntr,wf)
                    print('>>> recording japanese now...  ')
            else:
                # stop recording Japanese wavefile
                if pushflg_ja:
                    pushflg_ja = False
                    finish_wave_stream(wf,p,stream,name,from_target,to_target)
    
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
                    name = "./sound/sound" + str(cntr) + ".wav"
                    wf = wave.open(name,'w')
                    wf, p, stream = start_wave_stream(cntr,wf)
                    print('>>> recording english now...  ')
            else:
                # stop recording English wavefile
                if pushflg_en:
                    pushflg_en = False
                    finish_wave_stream(wf,p,stream,name,from_target,to_target)
            # wait
            sleep(0.5)
     
    except KeyboardInterrupt:
        pass
    f.close()

if __name__ == '__main__':
    main()
