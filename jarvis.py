import requests
import pyttsx3


def parse_text(text, starting_txt, end_txt, return_rounded_float=False):
    begin = text.find(starting_txt) + len(starting_txt)
    text = text[begin:]
    end = text.find(end_txt)
    if return_rounded_float:
        return str(round(float(text[:end]), 2))
    else:
        return text[:end]


def get_symbol_values(symbol):
    url = 'https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=' + symbol
    text = requests.get(url, timeout=10000).text
    # print(text)
    starting_string = 'last-trade-' + symbol
    end_string = '><'
    begin = text.find(starting_string) + len(starting_string)
    text = text[begin:]
    end = text.find(end_string)
    cut_text = text[:end]

    opening_value = parse_text(cut_text, 'data-open="', '"', True)
    current_value = parse_text(cut_text, 'data-last="', '"', True)
    engine.say('Kurs otwarcia' + symbol + ' wyniósł' + opening_value)
    engine.say('Aktualny kurs' + symbol + ' wynosi' + current_value)
    print(opening_value)
    print(current_value)


def get_wather():
    url = 'https://www.google.com/search?q=pogoda%20warszawa'
    text = requests.get(url, timeout=10000).text
    print(text)
    opady = parse_text(text, 'Szansa opadów:', '%')
    print(opady)


engine = pyttsx3.init()
get_symbol_values('ALLEGRO')
get_symbol_values('CDPROJEKT')
# get_wather()

engine.runAndWait()
