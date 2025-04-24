# Set audio device indices
# Usually, setting both to 1 will be valid default values.
# try other indices from the provided list if you have multiple input/output devices.
# When first running the program, you will get a list of indices.
INPUT_DEVICE_INDEX = 3
OUTPUT_DEVICE_INDEX = 1

# Set the names of the AI and the user
YOUR_NAME = "Marc"
CHAR_NAME = "Assistant"

# Describe the setting to the LLM
SYSTEM_PROMPT = "The following is a conversation between a human and an AI friend. You are the AI friend and respond like a humorous and friendly human. The human input may have transcription errors and require correction."

def PROMPT_FORMAT(tools=""):
    return f"""Format all of your output as json and strictly stick to the following variable names and structure. If a variable doesn't apply or is unclear/unknown, set it as NA.
{{
"response": Your response to {YOUR_NAME}. If using a tool, briefly explain what you will do. You must strictly stay in character.",
"tool": "required tool for the action (if any, must be one of {[tool.name for tool in tools]}",
"tool_input": "instructions for the tool task (if any)"
}}"""

# sets the default human input mode
# "voice": use speech as input
# "text": use text as input
INPUT_MODE = "voice"

# Set to true if you want to check your transcribed input before getting the LLM response
# If false, the answer will be returned directly.
CONFIRM_SEND = False

# Whether chatter in inactive mode will also be recorded in the database. Currently not supported!
LOG_CHATTER = False

# Whether to output AI responses as sound
PLAY_SOUND = True

# text to speech model for the AI audio output
# "silero" - fast and relatively accurate local model, recommended. The only fully compatible option with the script atm!
# "silero-server" - experimental model that is hosted on a server and can be accessed via an API. 
# "gtts" - standard robotic but accurate voice you hear using Google products
TTS_MODEL = "silero-server"

# TODO: use snowboy for hotword detection!
# words to active and exit the active mode
HOTWORD = "activate"
ENDWORD = "exit"

# STT engine to use
# "whisper" - local model loaded explicitly
# "distil-whisper" - local Whisper-derivate, significantly faster. English only.
# "silero" - local model loaded via torch.hub, not recommended
STT_MODEL_TYPE = "distil-whisper"

# Whisper model to use 
# check https://github.com/openai/whisper#available-models-and-languages for available models
# .en models only recognize English output, can be faster
if STT_MODEL_TYPE == "whisper":
    STT_MODEL = "small.en"
elif STT_MODEL_TYPE == "distil-whisper":
    STT_MODEL = "distil-whisper"

# LLM to use. 
# "local-openai" - a local model accessed via a local OpenAI-compatible API
# an OpenAI model, such as "gpt-3.5-turbo" (=ChatGPT)
LLM_NAME = "local-openai"

# Short and long key for the language you want to use for text to speech output.
# Languages other than English aren't currently supported
LANGUAGE = "english"
LANGUAGE_SHORT = "en"

# set the number of previous steps to store in the conversation history
HISTORY_STEPS = 200

# Whether to start in the inactive mode, requiring you to activate the AI using the hotword.
START_INACTIVE = False

# Whether to use MQTT for I/O on another device.
# If you choose mqtt mode, you will also need to pick BROKER_ADDRESS and BROKER_PORT further down.
MQTT_MIC = False
MQTT_SPEAKER = False

# address of the MQTT broker. If both ends are on the same device, "localhost" should be fine.
# If you don't have MQTT, install Mosquitto
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883  # Standard MQTT port

# address to host models
MODEL_HOSTING_ADDRESS = "localhost:5042"

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