# LachsBuddy 🐟
LachsBuddy is a conversational chatbot that allows you to converse with large language models (LLMs) using either voice or text. 

## Features
- talk or text with a LLM of your choice from Huggingface Hub, Bard or OpenAI
- TTS using gtts or Bark, STT using Whisper
- records background chatter if enabled
- manual copypasting mode to avoid using APIs and still converse using voice
- automatic output parsing/correction using Guidance
- logs sentiment, conversation history, prompt structure, timestamps, entities and more in a database
- provides a base for working with parametrized LLM outputs and further use cases such as robots, chatbots or assistants


## Installation
1. Install python (and create a new virtual environment if you wish).
2. Install ffmpeg and add to path. See [this manual](https://phoenixnap.com/kb/ffmpeg-windows) for detailed instructions.
3. Clone this repo, either by downloading it by pressing the green "code" button and extracting the zip somewhere or using the git clone command.
4. Open a terminal (type "cmd" in the Windows search bar or using Win + R). In the File Explorer, copy the path to the directory where you extracted this repository (the folder in which the readme.md file and the folders you see on the github main page are located). In the terminal, type "cd path" and replace path with the copied path. Execute that and then paste "pip install -r requirements.txt".
5. If you want to use local models and/or the Bark TTS library, you will also need to run "pip install -r requirements_extra.txt". Note that the preselected local model requires at least 11GB of VRAM, on a 12GB card it only lasts me about 8 conversation steps and wouldn't run with Bark at the same time. 

For the following steps, all the referred files are found in the "lachsbuddy" folder.

5. Run the main.py file (if you used the terminal till here, you can just type "cd lachsbuddy" and then "python main.py"). You will see a list of audio device IDs and API keys.
6. Open config.py and adjust anything to your preferences. You must specify your audio device indices at the top of the file, check the list obtained in the previous step for available device indices. 
7. Get an [OpenAI](https://platform.openai.com/account/api-keys), [Bard](https://github.com/dsdanielpark/Bard-API) or [Huggingface Hub](https://huggingface.co/docs/hub/security-tokens) key and paste it in keys.py. If you use a Huggingface Hub model, change the MODEL_NAME accordingly.
8. Run main.py again. You should now be able to converse.


## Usage
- when you run the main.py file, you may start in "inactive mode" if config.START_INACTIVE is set to True. This means that your voice input will be transcribed (and saved to a database if you enable LOG_CHATTER in the config) but you will not actively chat
- before you can converse then, you need to enter the "active mode" by saying/typing the hotword you specified. To exit and return to the inactive mode, say the endword. Both can be adapted in the config, but make sure that it's a word that's easy for you to pronounce and doesn't sound similar to other words so the speech recognizer picks it up reliably
- once you're in active mode, you can start conversing however you want. If you enabled CONFIRM_SEND in the config, you can review your transcribed input again before you will receive an answer. You can also use the commands that will be listed when you reach this stage. If LLM_CALLBACK_MODE is set to "manual", you will have to manually obtain the answer from a LLM such as ChatGPT and paste it back.
- you will now hear the response and the conversation step will be logged into the database located in the data directory.
- the conversation keeps going till you say/type the endword and return to inactive mode or close the script


## Limitations
- LLMs have general constraints such as context length or hallucinating facts. Therefore: Information may not be factual. There will be no memory of what you said in the beginning once you converse for long enough and there is also currently no memory of previous conversations.
- if not using Guidance: the LLM you choose must support a sufficiently complex parametrized output format. Currently, the output has to be dictionary-like, only OpenAI models seem reasonably reliable in sticking to that.
- inconsistent in character and instruction interpretation. Some prompts may break the output format
- local LLMs are likely to perform very badly
- Bark for text to speech tends to be slow and outputs may not be true to the actual text


## Upcoming features
- resume a past conversation
- provide a name for your AI
- voice recognition to distinguish speakers and have the AI recognize you by name and memory
- a web interface to interact with the database and have a visual representation of emotional interaction
- more complex sentiment analysis that is actually used to affect the LLM behavior and tone
- making past conversation information retrievable and utilize background chatter
- tools to allow searching the web, playing music, performing math, etc
- support for languages other than English
- setting up a vector database to use your own files as context
- integration into a physical robot and navigating/building context using a camera.
