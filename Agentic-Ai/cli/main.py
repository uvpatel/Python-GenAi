# Agentic AI with File Writing Capabilities

from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import json
import subprocess

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run_command(cmd: str):
    """Execute a shell command safely with limited permissions"""
    # Whitelist of safe commands
    safe_commands = ['ls', 'pwd', 'mkdir', 'touch', 'cat', 'tree', 'cd', 'rm']
    
    cmd_parts = cmd.split()
    if not cmd_parts or cmd_parts[0] not in safe_commands:
        return f"Error: Command '{cmd_parts[0] if cmd_parts else cmd}' not allowed. Safe commands: {', '.join(safe_commands)}"
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=10,
            cwd=os.getcwd()
        )
        output = result.stdout if result.stdout else result.stderr
        return output if output else "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def write_file(filepath: str, content: str):
    """Write content to a file, creating directories if needed"""
    try:
        # Get the directory path
        directory = os.path.dirname(filepath)
        
        # Create directory if it doesn't exist
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully created file: {filepath} ({len(content)} characters)"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def read_file(filepath: str):
    """Read content from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File: {filepath}\n\n{content}"
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_weather(city: str):
    """Get current weather for a city"""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return f"The weather in {city} is {response.text}."
        
        return f"Error: Unable to fetch weather (status code: {response.status_code})"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "write_file": write_file,
    "read_file": read_file
}

SYSTEM_PROMPT = """
You are a helpful AI Assistant who is specialized in resolving user queries.
You work on start, plan, action, observe mode.

For the given user query and available tools, plan the step by step execution, based on the planning,
select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

Wait for the observation and based on the observation from the tool call resolve the user query.

Rules:
- Follow the Output JSON Format EXACTLY.
- Always perform one step at a time and wait for next input
- Carefully analyze the user query
- When creating files, use write_file tool to actually create them
- For write_file, the input should be in format: "filepath|||content" where ||| separates path from content

Output JSON Format:
{
    "step": "string",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function"
}

Available Tools:
- "get_weather": Takes a city name as input and returns the current weather for the city
- "run_command": Takes linux command as a string and executes it. Safe commands: ls, pwd, mkdir, touch, cat, tree
- "write_file": Creates a file with content. Input format: "filepath|||content" (use ||| as separator)
- "read_file": Reads and returns the content of a file. Input: filepath

Example for creating files:
User Query: Create a todo app with HTML
Output: { "step": "plan", "content": "I need to create an HTML file for a todo app" }
Output: { "step": "action", "function": "run_command", "input": "mkdir -p todo_app" }
(observe mkdir result)
Output: { "step": "action", "function": "write_file", "input": "todo_app/index.html|||<!DOCTYPE html><html>...</html>" }
(observe write result)
Output: { "step": "output", "content": "Created todo app in todo_app folder with index.html" }
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

print("🤖 Agent ready! Type your query or 'exit' to quit.\n")

# Add debug flag
DEBUG = True

while True:
    try:
        query = input("> ")
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("👋 Goodbye!")
            break
            
        messages.append({"role": "user", "content": query})

        while True:
            try:
                response = client.chat.completions.create(
                    model="gemini-3-flash-preview",
                    response_format={"type": "json_object"},
                    messages=messages
                )

                assistant_content = response.choices[0].message.content
                messages.append({"role": "assistant", "content": assistant_content})
                
                if DEBUG:
                    print(f"DEBUG: {assistant_content}")
                
                parsed_payload = json.loads(assistant_content)

                # Gemini may sometimes return a list of step objects instead of a single object.
                if isinstance(parsed_payload, dict):
                    parsed_steps = [parsed_payload]
                elif isinstance(parsed_payload, list):
                    parsed_steps = [item for item in parsed_payload if isinstance(item, dict)]
                else:
                    print("❌ Invalid JSON response shape: expected object or list of objects")
                    break

                should_request_next_step = False
                has_final_output = False

                for parsed_response in parsed_steps:
                    step_type = parsed_response.get("step")

                    if step_type == "plan":
                        print(f"🧠: {parsed_response.get('content')}")
                        continue

                    if step_type == "action":
                        tool_name = parsed_response.get("function")
                        tool_input = parsed_response.get("input")
                        tool_input_str = "" if tool_input is None else str(tool_input)
                        preview = tool_input_str[:50] + ("..." if len(tool_input_str) > 50 else "")

                        print(f"🛠️: Calling {tool_name}('{preview}')")

                        if tool_name in available_tools:
                            # Special handling for write_file
                            if tool_name == "write_file":
                                # Parse the input: filepath|||content
                                if "|||" in tool_input_str:
                                    parts = tool_input_str.split("|||", 1)
                                    filepath = parts[0].strip()
                                    content = parts[1] if len(parts) > 1 else ""
                                    output = available_tools[tool_name](filepath, content)
                                else:
                                    output = "Error: write_file requires format 'filepath|||content'"
                            else:
                                output = available_tools[tool_name](tool_input_str)

                            print(f"✅: {output}")
                            messages.append({
                                "role": "user",
                                "content": json.dumps({"step": "observe", "output": str(output)})
                            })
                            should_request_next_step = True
                            continue

                        error_msg = f"Error: Tool '{tool_name}' not found"
                        print(f"❌ {error_msg}")
                        messages.append({
                            "role": "user",
                            "content": json.dumps({"step": "observe", "output": error_msg})
                        })
                        should_request_next_step = True
                        continue

                    if step_type == "output":
                        print(f"🤖: {parsed_response.get('content')}\n")
                        has_final_output = True
                        break

                    print(f"❌ Unknown step type: {step_type}")

                if has_final_output:
                    break

                if should_request_next_step:
                    continue

                print("❌ No actionable step produced by model")
                break
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Response was: {assistant_content}")
                break
            except Exception as e:
                print(f"❌ Error during agent loop: {e}")
                break
                
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        continue