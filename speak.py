from gtts import gTTS
import os
from playsound import playsound
import random
import string

def speak(text):
    print(f"🔊 Nova: {text}")
    filename = ''.join(random.choices(string.ascii_lowercase, k=10)) + ".mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    playsound(filename)
    os.remove(filename)
