from flask import Flask, redirect, url_for, render_template, request
import pyaudio
import wave
import openai
import speech_recognition as s
import gtts  
from playsound import playsound  
import time
import json
from json import JSONEncoder
import jsonpickle
import os
# import cred
from dotenv import load_dotenv
# from waitress import serve

class Thing(object):
    def __init__(self, name):
        self.name = name

app = Flask(__name__)


def configure():
    load_dotenv()


chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 10
filename = "output.wav"


 # Define OpenAI API key 
# openai.api_key = cred.api_key
openai.api_key = os.getenv('api_key')




def json_serializer(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8')

    return obj
     


@app.route("/")
@app.route("/index")
def page1():
    return render_template("index.html")

    # return "Hello"

@app.route("/record",methods=['POST','GET'])
def record():
    output = request.form.to_dict()
    print(output)
    name = output["name"]

    print("Recording for 10 seconds")
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    # frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')
    
    # Save the recorded data as a WAV file
    filename = "output.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # # Set up the model and prompt
    model_engine = "text-davinci-003"
    print("model")
    print(model_engine)
    # prompt = "Once upon a time, in a land far, far away, there was a princess who..."
    sr = s.Recognizer()
    # print("Speak something")
    query = []
    with s.WavFile('output.wav') as m:
        audio = sr.listen(m)
        query = sr.recognize_google(audio)
        print('query now')
        print(query)
    # print("Question to ChatGPT")
    # playsound("output.wav")  
    return render_template("record.html",query=query)
    # return {"members":["Member1","Member2"]}
query = []
frames = []  # Initialize array to store frames


@app.route("/output" ,methods=['POST','GET'])
def output():
    openai.api_key = os.getenv('api_key')
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # # Define OpenAI API key 
    # openai.api_key = "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"

    # Set up the model and prompt
    model_engine = "text-davinci-003"
    # prompt = "Once upon a time, in a land far, far away, there was a princess who..."
    sr = s.Recognizer()
    # print("Speak something")

    query = []
    with s.WavFile('output.wav') as m:
        audio = sr.listen(m)
        query = sr.recognize_google(audio)
        print(query)

    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=query,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print("Open AI Response")
    response = completion.choices[0].text
    print(response)
    
    
    print("Chat GPT Answer")
    t1 = gtts.gTTS(response,lang='hi')
    t1.save("welcome.mp3")   
    playsound("welcome.mp3")  
    output = completion.choices[0].text
    if os.path.exists("output.wav"):
        os.remove("output.wav")
    else:
        print("The file does not exist")

    return render_template("output.html", output=output)
    
# ***********************************************************************************************************

 

if __name__ == "__main__":
    configure()
    
    # serve(app, host="0.0.0.0", port=8080)
    # app.run(debug=False,host='0.0.0.0')
    app.run()