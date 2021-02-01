import pyaudio
import wave
import time
from datetime import datetime
from threading import Thread

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
            start_time = datetime.now()
            print("recording started", start_time)

            data = stream.read(RATE * RECORD_SECONDS, False)

            end_time = datetime.now()
            print("finished", end_time)

            name = f'{prefix}{start_time:%Y-%m-%d-%H-%M-%S.%f}-{end_time:%H-%M-%S.%f}.wav'
            # name = "out.wav"
            print("writing", name)
            with wave.open(name, 'wb') as waveFile:
                waveFile.setnchannels(CHANNELS)
                waveFile.setsampwidth(audio.get_sample_size(FORMAT))
                waveFile.setframerate(RATE)
                waveFile.writeframes(data)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


if __name__ == '__main__':
    Thread(target=recorder, args=('outputs/',)).start()
    time.sleep(1.5)
    Thread(target=recorder, args=('outputs/',)).start()