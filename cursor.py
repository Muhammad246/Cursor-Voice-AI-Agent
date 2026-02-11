import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
import json
import requests
import os
import speech_recognition as sr
from openai.helpers import LocalAudioPlayer
from openai import AsyncOpenAI

load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()

async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=speech,
        instructions="Speak in a cheerful manner and positive tone",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

def get_weather(city : str):
    url = f"http://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    
    if response.status_code == 200:
        return f"The Weather in {city} is {response.text}"
    
    return "Something went wrong"

# A tool which can run any kind of command on my system
def run_command(cmd: str):
    result = os.system(cmd)
    return result

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}


SYSTEM_PROMPT = """
    You are an expert AI Assistant in resolving user queries using chain of thought.
    You work on START, PLAN and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be of multiple steps. 
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of available tools.
    For every tool call wait for the observe step which is the output from the called tool.
    
    Rules:
    - Strictly follow the given JSON output format.
    - Only run one step at a time.
    - The sequence of steps are: 
      START(where user gives an input), 
      PLAN (That can be multiple times) and finally
      OUTPUT (Which is going to be displayed to the user).
      
    Output JSON Format:
      { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input" : "string" }
      
      Available Tools:
      - get_weather(city : str): Takes city name as an input string and return the weather info about the city.
      - run_command(cmd: str): Takes a system linux command as string and executes the command on user's system and returns the output from that command.
      
    Example 1:
      
      START: Hey, can you solve 2 + 3 * 5 / 10?      
      PLAN: { "step": "PLAN": "content": "Seems like users is interested in math problem }
      PLAN: { "step": "PLAN": "content": "Yes, the BODMAS is correct thing to be done here" }
      PLAN: { "step": "PLAN": "content": "First we must multiply 3 * 5 which is 15" }
      PLAN: { "step": "PLAN": "content": "Now, the new equation is 2 + 15 / 10" }
      PLAN: { "step": "PLAN": "content": "We must perform divide that is 15 / 10" }
      PLAN: { "step": "PLAN": "content": "Now the new equation is 2 + 1.5" }
      PLAN: { "step": "PLAN": "content": "Now, finally lets perform the addition 3.5" }
      PLAN: { "step": "PLAN": "content": "Great, we have solved and finally left with 3.5 as answer" }
      OUTPUT: { "step": "OUTPUT": "content": "3.5" }  
      
      Example 2:
      
      START: What is the weather of Karachi?      
      PLAN: { "step": "PLAN": "content": "Seems like users is interested in getting weather of pakistan }
      PLAN: { "step": "PLAN": "content": "Lets see if we have any available tool from the list of available tools" }
      PLAN: { "step": "PLAN": "content": "Great, we have get_weather tool available for this query" }
      PLAN: { "step": "PLAN": "content": "I need to call get_weather tool for karachi as input for city" }
      PLAN: { "step": "TOOL": "tool": "get_weather", "input": "karachi"}
      PLAN: { "step": "OBSERVE": "tool": "get_weather", "output": "the temp of karachi is cloudy with 20 C"}
      PLAN: { "step": "PLAN": "content": "Great, I got the weather info about karachi" }
      OUTPUT: { "step": "OUTPUT": "content": "The current weather in karachi is 20 C with some cloudy sky" }       
"""



class MyOutputFormat(BaseModel):
    step: str = Field(... , description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")
   
message_history = [
    { "role": "system", "content": SYSTEM_PROMPT },
]

r = sr.Recognizer()
with sr.Microphone() as source: # Mic Access
    
    r.adjust_for_ambient_noise(source) # removes background noise
    r.pause_threshold = 2 # starts recording after 2 sec pause from user
        
    while True:
    
        print("Speak Something...")
        audio = r.listen(source)
        
        print("Processing Audio... (STT)")
        user_query = r.recognize_google(audio)
        message_history.append({ "role": "user", "content": user_query })

        while True:
            response = client.chat.completions.parse(
            model = "gpt-4o", 
            response_format = MyOutputFormat,
            messages = message_history
            )
        
            raw_result = response.choices[0].message.content
            message_history.append({"role": "assistant", "content": raw_result})
            parsed_result = response.choices[0].message.parsed
            
            if parsed_result.step == "START":
                print("🔥", parsed_result.content)
                continue

            if parsed_result.step == "TOOL":
                tool_to_call = parsed_result.tool
                tool_input = parsed_result.input
                print(f"🧰: {tool_to_call} ({tool_input})")

                tool_response = available_tools[tool_to_call](tool_input)
                message_history.append({ "role": "developer", "content": json.dumps(
                    { "step": "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response}
                ) })
                continue

            if parsed_result.step == "PLAN":
                print("🧠", parsed_result.content)
                continue
            
            if parsed_result.step == "OUTPUT":
                print("🤖", parsed_result.content)
                asyncio.run(tts(speech=parsed_result.content))        
                break
