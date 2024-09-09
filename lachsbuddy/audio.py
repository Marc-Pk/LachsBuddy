'''Handles audio I/O'''

import speech_recognition as sr
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import config
import traceback
from keys import OPENAI_API_BASE, OPENAI_API_KEY
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import json
import base64


if config.STT_MODEL_TYPE == "whisper-api":
    import openai

if config.TTS_MODEL == "bark":
    from bark import generate_audio, SAMPLE_RATE
    import numpy as np

elif config.TTS_MODEL == "gtts":
    from gtts import gTTS

elif config.TTS_MODEL == "silero":
    import torch
    import sounddevice as sd
    import time

else:
    print("audio.py: Please provide a valid text to speech model for the TTS_MODEL variable.")

if config.STT_MODEL_TYPE == "silero":
    silero_stt, decode, utils = torch.hub.load(repo_or_dir = 'snakers4/silero-models',
                model='silero_stt', language='en',
                device="cpu", trust_repo=True)



def play_effect(file):
    '''This function plays a sound effect using the PyDub library.
    It takes a file path as input and plays the corresponding audio file.'''
    play(AudioSegment.from_file(file))


def play_tts(phrase, language_short=config.LANGUAGE_SHORT, playback_speed=1.2):
    '''This function converts text to speech using the Google Text-to-Speech (gTTS) API and plays the resulting audio.
    It takes three optional parameters:
    phrase is the text to convert to speech,
    language_short is the language to use (default is specified in the config module),
    playback_speed is the speed at which to play the audio (default is 1.4 times normal speed).
    If config.PLAY_SOUND is set to False, no audio will be played.'''
    # check if sound playback is enabled
    if config.PLAY_SOUND:
        try:
            # use gTTS to convert the text to a temporary audio file and store it in a byte stream
            if config.TTS_MODEL == "gtts":
                mp3_fp = BytesIO()
                gtts_audio = gTTS(text=phrase, lang=language_short)
                gtts_audio.write_to_fp(mp3_fp)
                mp3_fp.seek(0)

                # play the audio file, speeding it up if necessary
                play(AudioSegment.from_file(mp3_fp, format="mp3").speedup(playback_speed=playback_speed))
                mp3_fp.close()

            # use Bark to convert the text to a temporary audio file and store it in a byte stream
            elif config.TTS_MODEL == "bark":
                bark_audio_raw = generate_audio(phrase, history_prompt=f"v2/{language_short}_speaker_0")
                bark_audio_arr = (bark_audio_raw * np.iinfo(np.int16).max).astype(np.int16)

                bark_audio = AudioSegment(
                    data=bark_audio_arr.tobytes(),
                    sample_width=bark_audio_arr.dtype.itemsize,
                    frame_rate=SAMPLE_RATE,
                    channels=1)

                play(bark_audio.speedup(playback_speed=playback_speed))

            elif config.TTS_MODEL == "silero":
                language = 'en'
                speaker = 'v3_en'
                device = torch.device('cpu')
                sample_rate = 24000
                silero_tts,_ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                model='silero_tts',
                                language=language,
                                speaker=speaker,
                                device=device)
                silero_audio = silero_tts.apply_tts(text=phrase, sample_rate=sample_rate, speaker="en_117")
                
                if config.MQTT_SPEAKER:
                    audio = base64.b64encode(silero_audio.numpy()).decode()
                    publish.single("system/client-io", payload=str(json.dumps({"PLAY AUDIO": audio})), hostname=config.BROKER_ADDRESS)
                    
                    #publish.single("system/client-io", payload=str(json.dumps({"PLAY AUDIO":bytes(silero_audio.numpy())})))
                    print("sent audio")
                    confirmation = subscribe.simple("system/io-client", hostname=config.BROKER_ADDRESS).payload.decode()
                    print(confirmation)

                else:
                    sd.play(silero_audio, sample_rate)
                    sd.wait()
            else:
                raise Exception("Invalid TTS model, check TTS_MODEL in the config file.")

        except:
            traceback.print_exc()
            print("(Audio generation failed)")


def listen_mic(stt_model):
    global client
    '''
    This function listens to audio input from a microphone using the SpeechRecognition library.
    It takes a whisper speech to text model as input, which is used to transcribe the audio input.
    The function adjusts for ambient noise and prompts the user to speak before recording the audio.
    The resulting transcribed text string is returned as output.
    '''
    r = sr.Recognizer()

    # get audio from another device using MQTT
    if config.MQTT_MIC:
        publish.single("system/client-io", payload=json.dumps({"REQUESTING AUDIO":""}), hostname=config.BROKER_ADDRESS)
        print(config.style.MAGENTA + "Recording started, speak now" + config.style.RESET)
        raw_audio = subscribe.simple("speech/io-client", hostname=config.BROKER_ADDRESS).payload
        print(config.style.MAGENTA + "Recording complete" + config.style.RESET)
        audio = sr.AudioData((BytesIO(raw_audio).read()), 16000, 1)

    else:
        with sr.Microphone(device_index=config.INPUT_DEVICE_INDEX, sample_rate=16000) as source:
            r.adjust_for_ambient_noise(source)
            print(config.style.MAGENTA + "Recording started, speak now" + config.style.RESET)
            audio = r.listen(source)
            print(config.style.MAGENTA + "Recording complete" + config.style.RESET)
            

    # transcribe audio
    if config.STT_MODEL_TYPE == "whisper":
        transcribed_text = r.recognize_whisper(audio, model=stt_model, language = "en")

    # currently broken
    elif config.STT_MODEL_TYPE == "whisper-api":
        audio_file = BytesIO(audio.get_wav_data())

        whisper = openai.OpenAI(
            api_key=OPENAI_API_KEY, 
            base_url=OPENAI_API_BASE)

        transcribed_text = whisper.audio.transcriptions.create(model=stt_model, file=audio_file, response_format = "text")

    elif config.STT_MODEL_TYPE == "silero":
        audio = AudioSegment.from_file(BytesIO(audio.get_wav_data()))
        transcribed_text = decode(silero_stt(torch.FloatTensor(audio.get_array_of_samples()).view(1, -1))[0])  

    return transcribed_text


