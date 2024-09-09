# Set audio device indices
# Usually, setting both to 1 will be valid default values.
# try other indices from the provided list if you have multiple input/output devices.
# When first running the program, you will get a list of indices.
INPUT_DEVICE_INDEX = 2
OUTPUT_DEVICE_INDEX = 1

# sets the default human input mode
# "voice": use speech as input
# "text": use text as input
INPUT_MODE = "voice"

# Set to true if you want to check your transcribed input before getting the LLM response
# If false, the answer will be returned directly.
CONFIRM_SEND = False

# Whether chatter in inactive mode will also be recorded in the database.
LOG_CHATTER = True

# Whether to output AI responses as sound
PLAY_SOUND = True

# text to speech model for the AI audio output
# "silero" - fast and relatively accurate local model, recommended. The only fully compatible option with the script atm!
# "gtts" - standard robotic but accurate voice you hear using Google products
# "bark" - experimental model that may confabulate the output to an extent and is not very accurate
TTS_MODEL = "silero"

# words to active and exit the active mode
HOTWORD = "activate"
ENDWORD = "exit"

# STT engine to use
# "whisper" - local model loaded explicitly
# "whisper-api" - model loded via OpenAI-compatible API, can also be provided locally
# "silero" - local model loaded via torch.hub, not recommended
STT_MODEL_TYPE = "whisper"

# Whisper model to use 
# check https://github.com/openai/whisper#available-models-and-languages for available models
# .en models only recognize English output, can be faster
STT_MODEL = "base.en"

# LLM to use. 
# "local-openai" - a local model accessed via a local OpenAI-compatible API
# "bard" - Bard API - will likely be removed!
# an OpenAI model, such as "gpt-3.5-turbo" (=ChatGPT)
LLM_NAME = "local-openai"

# Short and long key for the language you want to use for text to speech output.
# Languages other than English aren't currently supported
LANGUAGE = "english"
LANGUAGE_SHORT = "en"

# set the number of previous steps to store in the conversation history
HISTORY_STEPS = 200

# emotions that should be distinguishable
EMOTION_LIST = ["neutral", "happiness", "fear", "anger", "surprise", "disgust", "sadness"]

VALID_VARIABLE_KEYS = ['human_input', 'human_emotion', 'reaction_emotion', 'intent', 'action', 'tool', 'tool_input',
                           'response', 'entities']

# Max tries for fixing the output parsing
LLM_PARSER_MAX_RETRIES = 0

# Whether to strart in the inactive mode, requiring you to activate the AI using the hotword
START_INACTIVE = False

########### MQTT
# Whether to use MQTT for I/O on another device.
# If you choose mqtt mode, you will also need to pick BROKER_ADDRESS and BROKER_PORT further down.
MQTT_MIC = False
MQTT_SPEAKER = False

# address of the MQTT broker. If both ends are on the same device, "localhost" should be fine.
# If you don't have MQTT, install Mosquitto
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883  # Standard MQTT port

########### Technical stuff, probably irrelevant for most users

# Define colors for printing

import os
os.system("")

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'