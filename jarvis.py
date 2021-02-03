import requests
import pyttsx3
import pandas as pd
from io import StringIO
import time
import datetime as dt
import investpy
import bitmex
import vlc
import time
import speech_recognition as sr
import pyaudio
import wave
import time
from datetime import datetime
from threading import Thread
from translate import Translator

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3


def recorder(prefix):
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT, channels=CHANNELS,
        rate=RATE, input=True,
    )
    try:
        while True:
            data = stream.read(RATE * RECORD_SECONDS, False)
            name = "out.wav"
            with wave.open(name, 'wb') as waveFile:
                waveFile.setnchannels(CHANNELS)
                waveFile.setsampwidth(audio.get_sample_size(FORMAT))
                waveFile.setframerate(RATE)
                waveFile.writeframes(data)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


def radio():
    url = 'https://radiostream.pl/tuba10-1.mp3'

    # define VLC instance
    # instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    instance = vlc.Instance()

    # Define VLC player
    player = instance.media_player_new()

    # Define VLC media
    media = instance.media_new(url)

    # Set player media
    player.set_media(media)

    # Play the media
    player.play()
    return player


def number(in_number):
    return format(in_number, ',g').replace(',', '*').replace('.', ',').replace('*', '.')


def parse_text(text, starting_txt, end_txt, return_rounded_float=False):
    begin = text.find(starting_txt) + len(starting_txt)
    text = text[begin:]
    end = text.find(end_txt)
    # print('___', text[:end], '___')
    if return_rounded_float:
        return round(float((text[:end]).replace(',', '')), 2)
    else:
        return text[:end]


def get_btc_usd(engine, say=False):
    headers = {
        'user-agent': "'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'"}
    text = requests.get('https://www.investing.com/crypto/bitcoin/btc-usd?cid=49798', timeout=10000,
                        headers=headers).text

    starting_string = '<span class="arial_22">BTC/USD</span>'
    end_string = '</div>'
    cut_text = parse_text(text, starting_string, end_string)
    # print(cut_text)

    current_value = parse_text(cut_text, '-last" dir="ltr">', '</span>', True)
    change_percentage = parse_text(cut_text, 'parentheses" dir="ltr">',
                                   '%</span>', True)

    if say:
        engine.say('Aktualny kurs btc/usd' + ' wynosi ' + number(current_value))
        engine.say('Zmiana wyniosła ' + number(change_percentage) + ' procent')
        print('Aktualny kurs', current_value)
        print('Zmiana ', change_percentage, '%')

    return current_value, change_percentage


def get_investing_values(symbol, say=False, engine=None):
    headers = {
        'user-agent': "'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'"}
    url = 'https://www.investing.com/equities/' + symbol.lower().replace(' ', '')
    try:
        text = requests.get(url, timeout=10000, headers=headers).text
    except Exception:
        print('Error: ', Exception)

    starting_string = '<div  class="left current-data">'
    end_string = 'Real-time derived data.'
    cut_text = parse_text(text, starting_string, end_string)

    current_value = parse_text(cut_text, 'id="last_last" dir="ltr">', '</span>', True)
    change_percentage = parse_text(cut_text, 'pid-37756-pcp parentheses" dir="ltr">',
                                   '%</span>', True)

    if say:
        engine.say('Aktualny kurs' + symbol + ' wynosi' + number(current_value) + ' złotych')
        engine.say('Zmiana' + symbol + ' wyniosła ' + number(change_percentage) + ' procent')
        print('Aktualny kurs', symbol, current_value)
        print('Zmiana ', symbol, change_percentage, '%')

    return current_value, change_percentage


def get_bankier_values(symbol, say=False):
    url = 'https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=' + symbol.lower().replace(' ', '')

    text = requests.get(url, timeout=10000).text
    # print(text)
    starting_string = 'last-trade-' + symbol.upper().replace(' ', '')
    end_string = '><'
    begin = text.find(starting_string) + len(starting_string)
    text = text[begin:]
    end = text.find(end_string)
    cut_text = text[:end]

    opening_value = float(parse_text(cut_text, 'data-open="', '"', True))
    current_value = float(parse_text(cut_text, 'data-last="', '"', True))
    if say:
        engine.say('Kurs otwarcia' + symbol + ' wyniósł' + str(opening_value) + ' złotych')
        engine.say('Aktualny kurs' + symbol + ' wynosi' + str(current_value) + ' złotych')
        print('Kurs otwarcia', symbol, opening_value)
        print('Aktualny kurs', symbol, current_value)

    return current_value, opening_value


def get_weather():
    translator = Translator(to_lang="pl")
    api_key = '3f53933116ae4b37adec5517033460e5'
    url = 'http://api.openweathermap.org/data/2.5/weather?q=warsaw&appid=' + api_key
    weather = requests.get(url, timeout=10000).json()
    print('Głowny ', translator.translate(weather['weather'][0]['main']))
    print('Opis', translator.translate(weather['weather'][0]['description']))
    text = 'Aktualna pogoda. ' + translator.translate(weather['weather'][0]['description'])
    # print(weather['weather']['description'])
    text += ', temperatura wynosi ' + str(round(float(weather['main']['temp'] - 273.16), 1)) + '°C'
    text += ', temperatura odczuwalna wynosi ' + str(round(float(weather['main']['feels_like'] - 273.16), 1)) + '°C'
    text += ', ciśnienie wynosi ' + str(number(round(float(weather['main']['pressure']), 1))) + ' hPa'
    text += ', wilgotność wynosi ' + str(number(round(float(weather['main']['humidity']), 1))) + '%'
    print(text)
    return text


def get_calendar(calendar_url):
    text = requests.get(calendar_url, timeout=10000).text
    calendar_text = parse_text(text, 'content="CalendarSheet', '"><meta name="google"').replace(',', ', ')
    print(calendar_text)
    engine.say(calendar_text)
    csv_file = StringIO(calendar_text)
    df = pd.read_csv(csv_file, sep=',')
    print(df)
    return df


#
#
# df = investpy.stocks.get_stock_information('CDR', 'poland', as_json=False)
# for i, col in enumerate(df):
#     print(col, df.iloc[0, i])


def speech_rec(r):
    # with sr.Microphone() as source:
    with sr.WavFile('out.wav') as source:
        audio = r.record(source)

        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`

            recognized_text = r.recognize_google(audio, language="pl-PL")
            print(recognized_text)
            return recognized_text
        except sr.UnknownValueError:
            # print("Google Speech Recognition could not understand audio")
            return 'nothing'
        except sr.RequestError as e:
            # print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return 'nothing'

        # try:
        #     recognized_text = r.recognize_google(audio_text, language="pl-PL")
        #     print("Text: " + recognized_text)
        #     return recognized_text
        # except:
        #     print("Sorry, I did not get that")
        #     return 'nothing'


def check_keywords(keywords, text):
    if all(x in text.lower() for x in keywords):
        return True
    else:
        return False


def get_bitmex_val(client):
    print(client.Quote.Quote_get(symbol="XBTUSD", reverse=True, count=1).result())


def main():
    bitmex_client = bitmex.bitmex()
    get_bitmex_val(bitmex_client)
    engine = pyttsx3.init()
    r = sr.Recognizer()
    r.energy_threshold = 100
    weather_text = get_weather()
    engine.say(weather_text)
    get_btc_usd(engine, True)
    # engine.say(dt.datetime.now())
    print(dt.datetime.now())
    # engine.say('Wpisy z kalendarza')
    # get_calendar('https://docs.google.com/spreadsheets/d/1qkuZfhWN2ZLHsSX0t2_ptC5geoDVSwy4O9dRpeh89NA/edit?usp=sharing')
    # get_investing_values('Allegro', True)

    current_val, opening_val = get_investing_values('CD Project', True, engine)
    engine.runAndWait()
    player = radio()
    player.stop()

    while True:
        command = speech_rec(r)
        new_val, change_val = get_investing_values('CD Project')
        if check_keywords(['włącz', 'radio'], command):
            player.play()
        elif check_keywords(['wyłącz', 'radio'], command):
            player.stop()
        elif check_keywords(['wartość', 'bitcoin'], command):
            get_btc_usd(engine, True)
            engine.runAndWait()
        elif check_keywords(['pogoda'], command):
            weather_text = get_weather()
            engine.say(weather_text)
            engine.runAndWait()
        if new_val / current_val > 1.01 or new_val / current_val < 0.99:
            if new_val / current_val > 1:
                engine.say('Wielki sukces polskiej prawicy')
            else:
                engine.say('Dramat')

            current_val = new_val
            print(dt.datetime.now())
            engine.say(
                'Aktualny kurs CD Project wynosi' + str(current_val) + ' złotych. Zmiana kursu dzisiaj to: ' + str(
                    change_val) + ' procent')
            engine.runAndWait()
            print('Zmiana ', current_val, change_val, "%")
        else:
            # print(new_val / current_val)
            pass

        # time.sleep(30)


if __name__ == '__main__':
    Thread(target=recorder, args=('outputs/',)).start()
    time.sleep(RECORD_SECONDS / 2)
    Thread(target=recorder, args=('outputs/',)).start()
    main()
