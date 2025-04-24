'''Handles LLM initialization and prompting'''

from keys import *
import config
from openai import OpenAI
from pydantic import BaseModel, Field

class ResponseFormat(BaseModel):
    response: str = Field(description="The response from the LLM.")
    tool: str = Field(description="The tool used by the LLM.")
    tool_input: str = Field(description="The input to the tool.")

class LLM:
    def __init__(self, model_name=config.LLM_NAME):
        self.model_name = model_name
        if "openai" in model_name:
            self.llm = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        
    def predict(self, prompt: str) -> str:
        if "openai" in self.model_name:
            return self._predict_openai(prompt)
        else:
            raise ValueError(f"Invalid model name: {self.model_name}")

    def _predict_openai(self, prompt: str) -> str:
        res = self.llm.beta.chat.completions.parse(
            model="gpt-3.5-turbo",
            messages=prompt,
            response_format=ResponseFormat
        ).choices[0].message.parsed

        #convert pydantic object to dict
        res = res.model_dump()
        print(res)
        return res


def baseline_prompt(transcribed_text, context=[], system_prompt=config.SYSTEM_PROMPT, tools=[]):
    '''Defines a prompt template that is used to interact with the LLM. It takes a transcribed text string, a list of tools,
    a tool descriptions string, a conversation history string, and a list of emotions as inputs.
    Returns a raw prompt template, a formatted prompt string and a list of valid variable keys.
    This function also defines the desired output format of the LLM.'''

    # Desired output format
    prompt_format = config.PROMPT_FORMAT(tools=tools)

    SYSTEM_PROMPT_FORMATTED = \
"""{system_prompt}\n
You have access to the following tools: {tools}\n
{prompt_format}
History of ongoing conversation:
"""

    # Assemble the fully formatted prompt based on input
    SYSTEM_PROMPT_FORMATTED = SYSTEM_PROMPT_FORMATTED.format(system_prompt=system_prompt, prompt_format=prompt_format, tools=tools)

    prompt_formatted = [{"role": "system", "content": SYSTEM_PROMPT_FORMATTED}]
    if context != []:
        for i in range(len(context)):
            prompt_formatted.append({"role": context[i]["role"], "content": context[i]["content"]})
    prompt_formatted.append({"role": "user", "content": transcribed_text})

    return prompt_formatted


def initialize_tools():
    '''
    Returns a list of tools available to the LLM and functions bound to them and a string that describes the tools.
    '''
    # dummy tool for now

    def calculator(a: float, b: float, operation: str) -> float:
        """Performs basic arithmetic operations."""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a / b
        else:
            raise ValueError("Invalid operation. Use 'add', 'subtract', 'multiply', or 'divide'.")

    class Tool(BaseModel):
        name: str = Field(description="The name of the tool.")
        description: str = Field(description="A short description of the tool.")
    tools = [
        Tool(name="calculator", description="A calculator that can perform basic arithmetic operations."),
    ]

    # assemble a string that describes the tools for the prompt
    tool_descriptions = ''.join([f'{tool.name}: {tool.description}\n' for tool in tools])
    return tools, tool_descriptions