'''Handles database setup and interaction.'''

import sqlite3
import config
from audio import play_effect

def connect_to_database():
    '''
    Connects to the conversation history database and creates a table to store conversation data if it doesn't exist.
    '''
    global c, conn
    conn = sqlite3.connect('.//data//conversation_history.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS conversation_history (
                conversation_id INTEGER,
                step INTEGER,
                timestamp DATETIME,
                model TEXT,
                prompt_template TEXT,
                prompt_formatted TEXT,
                human_input TEXT,
                llm_output_raw TEXT,
                ai_response TEXT,
                tool TEXT DEFAULT 'NA',
                tool_input TEXT DEFAULT 'NA',
                context TEXT,
                listening_mode TEXT,
                PRIMARY KEY (conversation_id, step))''')
    conn.commit()


def get_current_history():
    '''
    Retrieves conversation history from the database based on the specified number of steps.
    Returns a formatted string with the conversation history.
    '''
    context = []
    cursor = conn.execute(f"""SELECT 
                            human_input, 
                            ai_response 
                            FROM conversation_history 
                            WHERE conversation_id = (SELECT MAX(conversation_id) 
                                FROM conversation_history) 
                            AND step >= (SELECT MAX(step) 
                                FROM (SELECT step FROM conversation_history 
                                WHERE conversation_id = (SELECT MAX(conversation_id) 
                                FROM conversation_history)))-{config.HISTORY_STEPS} 
                            ORDER BY step""")

    # get SQL results and assemble list
    # turn into a dict with keys "user" and "assistant"

    for row in cursor.fetchall():
        context.append({"role": "user", "content": row[0]})
        context.append({"role": "assistant", "content": row[1]})
        #context.append({"user": {f"{config.YOUR_NAME}: ": row[0]}}, {"assistant": {f"{config.CHAR_NAME}: ": row[1]}})

    return context


def insert_chatter(timestamp, transcribed_text, listening_mode):
    '''inserts chatter into the database.
    Takes a datetime timestamp, the transcribed text as a string and the current listening mode as a string.'''
    c.execute("INSERT INTO conversation_history (timestamp, human_input_raw, listening_mode) VALUES (?, ?, ?)",
              (timestamp, transcribed_text, listening_mode))
    conn.commit()


def insert_conversation(conversation_id, step, timestamp, model, prompt_template, prompt_formatted,
                                transcribed_text, llm_output_raw, llm_output_dict, context, listening_mode):
    '''
    Inserts a row into the conversation history table with all relevant information for the current step in the conversation.
    conversation_id: The ID of the conversation (unique identifier).
    step: The step number of the current interaction.
    timestamp: A datetime timestamp of the current interaction.
    prompt_formatted: The formatted prompt for the current interaction.
    transcribed_text: The user input as a string.
    llm_output_dict: A dictionary of the LLM output with different attributes.
    context: A string of the conversation history.
    listening_mode: The listening mode at the time of the input as a string.
    '''
    c.execute(
        """INSERT INTO conversation_history (conversation_id, step, timestamp, prompt_formatted, human_input, ai_response, tool, tool_input, context, listening_mode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (conversation_id, step, timestamp,
         str(prompt_formatted), transcribed_text, 
         llm_output_dict['response'],
         str(llm_output_dict['tool']).lower(),
         str(llm_output_dict['tool_input']),
         str(context), 
         listening_mode))

    conn.commit()



def start_new_conversation():
    '''Sets metadata for a new active conversation.
    Returns the step as 0, an empty conversation history, listening mode set to "active",
    generates a new conversation_id and prints out info as well as playing a sound.'''
    step = 0
    context = []
    listening_mode = "active"

    # create new conversation_id, set to 1 if none available
    try:
        c.execute('SELECT MAX(conversation_id) FROM conversation_history')
        conversation_id = int(c.fetchone()[0]) + 1

    except TypeError:
        conversation_id = 1

    play_effect(r"resources/enable_active_mode.wav")
    print(config.style.MAGENTA + f"Hotword recognized, active mode enabled. If you want to return to inactive mode, say the endword '{config.ENDWORD}'" + config.style.RESET)

    return step, context, listening_mode, conversation_id
