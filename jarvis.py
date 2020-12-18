import requests
import pyttsx3
import pandas as pd
from io import StringIO
import time
import datetime as dt


def parse_text(text, starting_txt, end_txt, return_rounded_float=False):
    begin = text.find(starting_txt) + len(starting_txt)
    text = text[begin:]
    end = text.find(end_txt)
    if return_rounded_float:
        return round(float(text[:end]), 2)
    else:
        return text[:end]


def get_investing_values(symbol, say=False):
    headers = {
        'user-agent': "'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'"}
    url = 'https://www.investing.com/equities/' + symbol.lower().replace(' ', '')
    text = requests.get(url, timeout=10000, headers=headers).text

    starting_string = '<div  class="left current-data">'
    end_string = 'Real-time derived data.'
    cut_text = parse_text(text, starting_string, end_string)

    current_value = parse_text(cut_text, 'id="last_last" dir="ltr">', '</span>', True)
    change_percentage = parse_text(cut_text, '<span class="arial_20 redFont  pid-37756-pcp parentheses" dir="ltr">', '%</span>', True)

    if say:
        engine.say('Aktualny kurs' + symbol + ' wynosi' + str(current_value) + ' złotych')
        engine.say('Zmiana' + symbol + 'wyniosła ' + symbol + str(change_percentage) + ' procent')
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


def get_wather():
    url = 'https://www.google.com/search?q=pogoda%20warszawa'
    text = requests.get(url, timeout=10000).text
    print(text)
    opady = parse_text(text, 'Szansa opadów:', '%')
    print(opady)


def get_calendar(calendar_url):
    text = requests.get(calendar_url, timeout=10000).text
    calendar_text = parse_text(text, 'content="CalendarSheet', '"><meta name="google"')
    print(calendar_text)
    engine.say(calendar_text)
    csv_file = StringIO(calendar_text)
    df = pd.read_csv(csv_file, sep=',')
    print(df)
    return df


engine = pyttsx3.init()
# engine.say(dt.datetime.now())
print(dt.datetime.now())
get_calendar('https://docs.google.com/spreadsheets/d/1qkuZfhWN2ZLHsSX0t2_ptC5geoDVSwy4O9dRpeh89NA/edit?usp=sharing')
# get_investing_values('Allegro', True)

current_val, opening_val = get_investing_values('CD Project', True)
engine.runAndWait()
while True:
    new_val, change_val = get_investing_values('CD Project')
    if new_val / current_val > 1.01 or new_val / current_val < 0.99:
        current_val = new_val
        engine.say('Aktualny kurs cdproject wynosi' + str(current_val) + ' złotych. Zmiana kursi dzisiaj to: ' + str(change_val) + ' procent')
        engine.runAndWait()
        print('zmiana ', current_val)
    else:
        print(new_val / current_val)

    time.sleep(10)

# get_wather()
