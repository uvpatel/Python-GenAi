from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
import os

load_dotenv()

# Must be AsyncOpenAI, not OpenAI
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    name="Test Agent",
    instructions="You are a helpful assistant that answers questions about geography.",
    model=OpenAIChatCompletionsModel(          # ← wire in custom client here
        model="gemini-1.5-flash-latest",
        openai_client=client
    )
)

result = Runner.run_sync(agent, "What is the capital of France?")
print(result.final_output)