from agents import Agent, Runner
from dotenv import load_dotenv
from google import genai
from google.genai import types


from pathlib import types

load_dotenv()
# Configure the client and tools
client = genai.Client()
tools = types.Tool(function_declarations=[schedule_meeting_function])
config = types.GenerateContentConfig(tools=[tools])



agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)


