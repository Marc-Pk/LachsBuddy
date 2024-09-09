'''Handles LLM initialization and prompting'''

from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import Tool
from keys import *
import config

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
import openai


def llm_chain(model_name=config.LLM_NAME):
    '''Takes a LLM name as input and returns an instance of the LLMChain class to be used as a model.'''
    if "openai" in model_name: 
        return openai.OpenAI(
            api_key=OPENAI_API_KEY, 
            base_url=OPENAI_API_BASE)

    elif model_name == "bard":
        from bardapi import Bard
        from typing import Any, List, Mapping, Optional
        bard = Bard(token_from_browser=True)
        class BardLLM(LLM):

            # create a custom LLM
            @property
            def _llm_type(self) -> str:
                return "custom"

            def _call(self,
                      prompt: str,
                      stop: Optional[List[str]] = None,
                      run_manager: Optional[CallbackManagerForLLMRun] = None,
                      ) -> str:
                if stop is not None:
                    raise ValueError("stop kwargs are not permitted.")

                # only return the answer key of the response
                bard_answer = bard.get_answer(prompt)
                if bard_answer["code"]:
                    return bard_answer["code"]
                else:
                    return bard_answer["content"]

        model_name = BardLLM(**{"bard":bard})

    # use an empty arbitrary prompt and return the model
    return LLMChain(prompt=PromptTemplate(template="{text}", input_variables=["text"]), llm=model_name)


def baseline_prompt(transcribed_text, tools="", tool_descriptions="", conv_history="", repair_attempt=False, emotion_list=config.EMOTION_LIST, valid_variable_keys= config.VALID_VARIABLE_KEYS):
    '''Defines a prompt template that is used to interact with the LLM. It takes a transcribed text string, a list of tools,
    a tool descriptions string, a conversation history string, and a list of emotions as inputs.
    Returns a raw prompt template, a formatted prompt string and a list of valid variable keys.
    This function also defines the desired output format of the LLM.'''

    # Describe the setting to the LLM
    PROMPT_MODE = "The following is a conversation between a human and an AI friend. You are the AI friend and respond like a humorous and friendly human. The human input may have transcription errors and require correction."
    
    # Desired output format
    PROMPT_OUTPUT_SPECS = f"""Format all of your output as json and strictly stick to the following variable names and structure. If a variable doesn't apply or is unclear/unknown, set it as NA. Avoid non-alphanumeric characters:
{{
"{valid_variable_keys[0]}": raw current human input, correct possible transcription errors if necessary,
"{valid_variable_keys[1]}": human input emotion, must be one of {emotion_list},
"{valid_variable_keys[2]}": expected emotion of another human in reaction to the human input, must be one of {emotion_list},
"{valid_variable_keys[3]}": intent of the human input,
"{valid_variable_keys[4]}": action for the AI,
"{valid_variable_keys[5]}": required tool for the action (if any, must be one of {[tool.name for tool in tools]},
"{valid_variable_keys[6]}": input for the tool (if any),
"{valid_variable_keys[7]}": verbal response to human input in tone of reaction_emotion, should not be longer than necessary. If using a tool, briefly explain what you will do,
"{valid_variable_keys[8]}": entities or places mentioned by the human or ai.
}}"""

    PROMPT_OUTPUT_SPECS_GUIDANCE = '''
```json
{
    human_input: {{human_input}},
    human_emotion: "{{select "human_emotion" options=emotion_list}}",
    reaction_emotion: "{{select "reaction_emotion" options=emotion_list}}",
    intent: "{{gen "intent" max_tokens=150 stop='\n'}}",
    action: "{{gen "action" max_tokens=150 stop='\n'}}",
    tool: "{{gen "tool" max_tokens=10 stop='\n'}}",
    tool_input: "{{gen "tool_input" max_tokens=10 stop='\n'}}",
    response: "{{gen "response" max_tokens=200 stop='\n'}}",
    entities: "{{gen "entities" max_tokens=20 stop='\n'}}"
}
```
'''

    # Stitch the specifications together
    if repair_attempt:
        PROMPT_TEMPLATE = \
"""You have to fix an AI generated chatbot answer. \n
Here is a wrongly parametrized AI generated answer of a chatbot:

{transcribed_text}

To be parsed correctly, the answer needs to be a python dictionary strictly in the following format. Transform the above answer accordingly and remove any newlines or bullet points within values but keep newlines between keys.

{PROMPT_OUTPUT_SPECS}"""

        # Creates a langchain PromptTemplate
        prompt = PromptTemplate(
            input_variables=["PROMPT_OUTPUT_SPECS", "transcribed_text"],
            template=PROMPT_TEMPLATE)

        prompt_formatted = prompt.format(PROMPT_OUTPUT_SPECS=PROMPT_OUTPUT_SPECS, transcribed_text=transcribed_text)
        #print("Repair prompt: --------- \n" + prompt_formatted)

    else:
        PROMPT_TEMPLATE = \
"""{PROMPT_MODE}\n
You have access to the following tools: {tool_descriptions}\n
{PROMPT_OUTPUT_SPECS}
History of ongoing conversation: \n{conv_history}\n
Raw current human input: {transcribed_text}\n
"""

        # Creates a langchain PromptTemplate
        prompt = PromptTemplate(
            input_variables=["PROMPT_MODE", "PROMPT_OUTPUT_SPECS", "conv_history", "transcribed_text",
                             "tool_descriptions"],
            template=PROMPT_TEMPLATE)

        # Assemble the fully formatted prompt based on input
        prompt_formatted = prompt.format(PROMPT_MODE=PROMPT_MODE, PROMPT_OUTPUT_SPECS=PROMPT_OUTPUT_SPECS,
                                         conv_history=conv_history, transcribed_text=transcribed_text,
                                         tool_descriptions=tool_descriptions)


    return prompt, prompt_formatted


def initialize_tools():
    '''
    Returns a list of tools available to the LLM and functions bound to them and a string that describes the tools.
    '''
    # set available tools
    tools = [
        Tool(
            name="Websearch",
            func=lambda x: 1,  # placeholder
            description="Ignore for now"
        ),
    ]

    # assemble a string that describes the tools for the prompt
    tool_descriptions = ''.join([f'{tool.name}: {tool.description}\n' for tool in tools])
    return tools, tool_descriptions