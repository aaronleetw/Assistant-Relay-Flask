from flask import *
from flask_mobility import Mobility
import requests
import speech_recognition as sr
import os

app = Flask(__name__, static_url_path='/static')
Mobility(app)
places = {'Back door', 'Library', 'Stair', 'Living room'}


def download_wav(url):
    os.remove('./response.wav')
    r = requests.get(url)
    with open('./response.wav', 'wb') as f:
        f.write(r.content)


def makePOST(cmd):
    url = 'http://172.16.242.5:3000/assistant'
    payload = {
        'command': cmd,
        'user': 'Aaron',
        "converse": False
    }
    response = requests.post(url, json=payload).json()
    if response['response'] == "":
        r = sr.Recognizer()
        download_wav('http://localhost:3000'+response['audio'])
        with sr.AudioFile('./response.wav') as source:
            audio = r.record(source)
        try:
            res = r.recognize_google(audio)
            if ' on' in res:
                return "on"
            elif ' off' in res:
                return "off"
            elif "isn't available" in res:
                return "offline"
            else:
                return "!ERROR!"
        except sr.UnknownValueError:
            print("!ERROR! Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "!ERROR! Could not request results from Google Speech Recognition service; {0}".format(e))


@app.route('/', methods=['GET'])
def index():
    res = {}
    for p in places:
        res[p] = makePOST("is " + p + " light on")
    return render_template('mainpage.html', places=res)


@ app.route('/status/<place>', methods=['GET'])
def status(place):
    if place == "all":
        res = {}
        for p in places:
            res[p] = makePOST("is " + p + " light on")
        return res
    return makePOST("is " + place + " light on")


@ app.route('/on/<place>', methods=['GET'])
def on(place):
    if place == "all":
        res = {}
        for p in places:
            res[p] = makePOST("turn on " + p + " light")
        return res
    return makePOST("turn on " + place)


@ app.route('/off/<place>', methods=['GET'])
def off(place):
    if place == "all":
        res = {}
        for p in places:
            res[p] = makePOST("turn off " + p + " light")
        return res
    return makePOST("turn off " + place + " light")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
