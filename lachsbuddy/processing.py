'''Handles the processing of I/O and calls to the LLM or database'''

import datetime
import re
from audio import *
from database import *
from llm import *
import config
import traceback
import json


def check_config():
    '''This function checks the config.py file to ensure that the input and output device indices are correctly set.
    If they are not set, the function raises an exception that prompts the user to set the correct values.
    The function also checks the keys.py file to ensure that the API keys for
    OpenAI or Huggingface are provided, and prompts the user to provide valid keys if necessary.
    '''
    errors = []
    if config.INPUT_DEVICE_INDEX < 0 or config.OUTPUT_DEVICE_INDEX < 0:
        import pyaudio
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        j = 0
        print("Audio indices: ")

        for i in range(0, num_devices):

            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

            if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                print("Output Device id ", j, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
                j += 1
        errors.append(
            "\nconfig.py: Please set the audio input/output device indices. The printed list shows your available device indices.")


    if OPENAI_API_KEY == "" and "openai" in config.LLM_NAME:
        errors.append(
            "keys.py: Please provide a valid OpenAI key or alternatively a dummy for a local OpenAI-compatible API as well as a base_url where the API is hosted.")

    if BARD_API_KEY == "" and config.LLM_NAME == "bard":
        errors.append(
            "keys.py: Please provide a valid Bard API key or use an OpenAI-compatible API instead by changing the LLM_NAME in config.py and providing a key/base_url in keys.py.")

    if len(errors) > 0:
        raise Exception('\n'.join(errors))


def get_llm_response(llm, transcribed_text, prompt, confirm_send=config.CONFIRM_SEND):
    ''' This function gets the response from the language model based on the input prompt and the mode set in the config.py file.
    Returns raw llm output and the parsed output dict
    It takes in the following parameters:

    llm: The language model to use for generating a response
    transcribed_text: The transcribed text from the user's voice input
    prompt: The prompt to use for generating a response

    confirm_send: A boolean value that indicates whether to confirm before sending the text to the language model or not.
    If set to True, the function prompts the user to confirm whether they want to send the transcribed text to the language model or not.
    If confirm_send is False, the function directly sends the text to the language model and returns the response.'''
    # manual copypasting to and from chatgpt
    retries = 0


    # confirm to send the transcribed text before sending if desired
    if confirm_send == True:

        llm_output_raw = input(config.style.MAGENTA +
                                "Type 'r' to re-record human input, 'e' to exit active mode, or anything else to send the input to the llm. Then press the 'Enter' key." + config.style.GREEN +
                                "\nTranscribed voice input: " + transcribed_text + config.style.RESET + "\n")

        # retry or exit
        if llm_output_raw == "r" or llm_output_raw == "e":
            return llm_output_raw, llm_output_raw

    print(config.style.GREEN + "\nTranscribed voice input: " + transcribed_text + config.style.RESET + "\n")
    # try to get a valid response till fixed or an error is raised
    while True:

        llm_output_raw = llm.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], 
            max_tokens=300,
            temperature=0.7,
            model="gpt-3.5-turbo",
            extra_body={"grammar_string":open("./grammars/json.gbnf").read(),
            "repetition_penalty":1.15,
            "top_k":0.9,
            "stopping_strings":["<|im_end|>", "}"],
            }).choices[0].message.content
                    
        #print("Raw output: \n" + llm_output_raw)
        # fetch a new response
        try:
            llm_output_dict = parse_output(llm_output_raw, prompt)
            if llm_output_dict != "f":
                return llm_output_dict, llm_output_raw

        # retry if parsing fails and the maximum number of retries is not reached
        except:
            retries += 1
            traceback.print_exc()
            print(f"Output parsing failed, attempt {retries}/{config.LLM_PARSER_MAX_RETRIES} to generate a new prompt.")


def parse_output(output_raw, prompt):
    '''
    This function takes in the raw output string from a language model and separates it into key-value pairs as specified in valid_variable_keys.
    Returns a dictionary containing the keys specified in valid_variable_keys and attempts to parse values for them from the output_raw string.
    '''
    print("raw output for formatting:\n" + output_raw)
    # check for newline characters
    if '\n' not in output_raw:
        for key in config.VALID_VARIABLE_KEYS:
            output_raw = re.sub(r'\b' + key + r'\b', '\n' + key, output_raw)

    # split by newline characters
    output_lines = output_raw.split('\n')

    # create dict with all values set to None
    output_dict = {key: "" for key in config.VALID_VARIABLE_KEYS}
    output_dict["response"] = None

    # split each of the separated lines into key/value pairs
    for line in output_lines:
        if '}' in line:
            break
        # remove trailing commas
        if line.endswith(',\n'):
            line = line[:-1]
        # remove trailing commas
        if line.endswith('"') or line.endswith("'",):
            line = line[:-1]

        # remove artifacts and match keys to specified keys
        if any(key in line for key in config.VALID_VARIABLE_KEYS) and len(line) > 3:
            key, value = line.replace('"', "").replace('str = ', "").replace('list = ', "").split(':')
            key = key.strip().lower().replace(' ', '_')
            if key in config.VALID_VARIABLE_KEYS:
                #print("Detected key " + key + " with value "+ value)
                output_dict[key] = value.strip() if value.strip().lower() != 'na' else ""

    if output_dict["response"] != None:
        print("Response parsed successfully")
        return output_dict

    else:
        print("Response couldn't be parsed")
        raise Exception("Response couldn't be parsed")

        # Attempt to re-enter the output
        # except:
        #     try:
        #         #try to fix the output as many times as specified in the config
        #         if retries < config.LLM_PARSER_MAX_RETRIES:
        #             retries += 1
        #             print(f"Attempt {retries}/{config.LLM_PARSER_MAX_RETRIES} to fix output parsing")
        #             _, prompt_formatted = baseline_prompt(output_raw, repair_attempt=True)
        #             #print("---------------------:\n"+ prompt_formatted+"\-----------------------------------------")
        #             output_raw = llm.run(prompt_formatted)
        #             print(f"\nOutput after fix {retries}: \n{output_raw}")
        #             #time.sleep(3)

        #     except:
        #         #traceback.print_exc()
        #         continue


def get_human_input(listening_mode, stt_model, log_chatter=config.LOG_CHATTER):
    '''
    Function to get the human input as a string. Parameters:
    input_mode: "voice" or "text", specifying the input medium
    listening_mode: "active" or "passive": Specify the current mode
    model: STT model, must be a whisper model name.
    log_chatter: Boolean. Whether to log chatter or not.

    Returns the transcribed text and a timestamp.
    '''

    #global the input mode to switch input mode permanently if the user changes it
    global input_mode
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if input_mode == "voice":
        # listen for audio input from the microphone
        transcribed_text = listen_mic(stt_model=stt_model)

        # switch to text input mode if the user says "text"
        if "Text." in transcribed_text:
            input_mode = "text"
            return get_human_input(listening_mode, stt_model)

        # log the conversation history if logging is enabled and the listening mode is passive
        if log_chatter == True and transcribed_text != "" and listening_mode == "passive":
            insert_chatter(timestamp, transcribed_text, listening_mode)


    elif input_mode == "text":
        # prompt the user to enter text input
        transcribed_text = str(input(config.style.MAGENTA + "Write a text message: " + config.style.RESET))

        # switch to voice input mode if the user says "voice". Currently not working.
        if transcribed_text == "voice":
            input_mode = "voice"
            return get_human_input(listening_mode, stt_model)

    else:
        # raise an exception if an invalid input mode is specified
        raise Exception("Invalid input mode in config.INPUT_MODE")

    return transcribed_text, timestamp


def startup_checks():
    '''Function for startup routines. Performs a config check and prints a welcome message'''
    global input_mode
    check_config()
    input_mode = config.INPUT_MODE
    if config.START_INACTIVE:
        print(config.style.MAGENTA + f"Welcome. You are currently in the inactive mode. Say the hotword '{config.HOTWORD}' to enter active mode" + config.style.RESET)
    else:
        pass


def run_in_background():
    '''
    Function for the inactive mode. Listens to voice/text input as specified and records it in the database if desired.
    '''
    connect_to_database()

    if config.START_INACTIVE:
        # get human input
        transcribed_text, timestamp = get_human_input(listening_mode="passive",
                                                      stt_model=config.STT_MODEL)
        print(config.style.BLUE + "Background chatter: " + transcribed_text + config.style.RESET)

    # Check if the hotword is mentioned, enable active mode in that case.
        if config.HOTWORD in transcribed_text.lower():
            run_conversation()
    else:
        run_conversation()


def run_conversation():
    '''loop for the active mode. Prompts the user for input and provides a back and forth interaction with a LLM, on terms specified in the config.'''
    # initialize LLM
    global tools, tool_descriptions, llm

    #initialize the LLM and tools
    llm = llm_chain(model_name=config.LLM_NAME)
    tools, tool_descriptions = initialize_tools()

    # initialize new conversation metadata
    step, conv_history, listening_mode, conversation_id = start_new_conversation()

    while True:
        #transcribed_text, timestamp = "Test?", datetime.datetime.strptime("09/19/23 13:55:26", '%m/%d/%y %H:%M:%S') #For testing
        transcribed_text, timestamp = get_human_input(listening_mode, stt_model=config.STT_MODEL)
        # return to inactive mode if endword is mentioned
        if config.ENDWORD in transcribed_text.lower():
            print(config.style.MAGENTA + "Endword recognized, returning to background mode" + config.style.RESET)
            listening_mode = "passive"
            break

        # fetch most recent history unless the conversation just started
        if step != 0:
            conv_history = get_current_history()

        # assemble the prompt
        prompt_template, prompt_formatted = baseline_prompt(transcribed_text, conv_history=conv_history)

        # get the llm response to the human input, re-record if wished and checking is enabled
        llm_output_dict, llm_output_raw = get_llm_response(llm=llm, transcribed_text=transcribed_text, prompt=prompt_formatted)
        if llm_output_dict == "r":
            continue

        elif llm_output_dict == "e":
            print(
                config.style.MAGENTA + f"You are now in the inactive mode again. Say the hotword '{config.HOTWORD}' to enter active mode" + config.style.RESET)
            break

        # insert into DB
        insert_conversation(conversation_id, step, timestamp, config.LLM_NAME, prompt_template, prompt_formatted,
                            transcribed_text, llm_output_raw, llm_output_dict, conv_history, listening_mode)

        # print and play output
        print(config.style.RED + "AI: " + llm_output_dict['response'] + config.style.RESET)
        play_tts(llm_output_dict['response'])
        step += 1
