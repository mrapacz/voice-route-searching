import os
import logging
import subprocess
from time import time

from config import *
from jakdojade import search_jakdojade
from semantics import analyze_command

logging.basicConfig(level=logging.INFO)
import speech_recognition as sr

RECORDINGS = ".cache"
FILENAME = "recording.wav"


def log_event(msg, lang="en", verbose=VOICE):
    print(msg)
    # logging.info(msg)

    # if verbose:
    #     say(msg, lang)


def send_to_asr_api(filename=FILENAME):
    log_event("Sending the command to ASR API")
    command = "{binary} -P {port} -p '{bearer}' -addr {addr} -w {filename} -verbose".format(
        binary=BINARY,
        port=PORT,
        bearer=BEARER,
        addr=ADDR,
        filename=filename,
    )

    output = subprocess.check_output(command, shell=True)
    command = output.decode().strip().split("\n")[-2]

    log_event(command, lang="pl")
    return command


def say(text, lang, prefix=None):
    if prefix:
        say(text=prefix, lang=lang)

    voice = "Zosia" if lang == "pl" else "Victoria"
    os.system('say -v {} "{}"'.format(voice, text))


def get_new_filepath():
    timestamp = str(int(time()))
    return os.path.join(RECORDINGS, timestamp) + ".wav"


def record():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        log_event("Listening...")
        audio = r.listen(source)

    filepath = get_new_filepath()
    log_event("Saving the recording to " + filepath, verbose=False)

    with open(filepath, "wb") as f:
        f.write(audio.get_wav_data(convert_rate=16000))

    return filepath


if __name__ == '__main__':
    filepath = record()
    command = send_to_asr_api(filename=filepath)
    # command = send_to_asr_api(filename=".cache/1548089603.wav")

    start, end = analyze_command(command)

    # end = None
    search_jakdojade(start, end, headless=False)
