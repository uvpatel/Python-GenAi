# 🤖 Agentic AI CLI - Interactive AI Agent with Tool Integration

An intelligent command-line agent powered by Google's Gemini API that can plan, execute actions, and resolve complex user queries using a set of available tools.

## 📋 Overview

This is an **agentic AI system** that operates in a **Plan → Action → Observe → Repeat** cycle. It acts as an intelligent assistant that can:
- Understand natural language queries
- Break down problems into steps
- Execute tools to accomplish tasks
- Learn from results and refine its approach
- Generate files and execute commands
- Provide intelligent responses

The agent uses Google's Gemini API (compatible with OpenAI client) and operates in strict JSON format for predictable behavior.

---

## 🏗️ Architecture & How It Works

### Core Concept: Plan-Action-Observe Loop

```
User Query
    ↓
Agent Plans Steps
    ↓
Agent Executes Action (Tool Call)
    ↓
Observe Results
    ↓
Refine & Continue or Output Final Answer
```

### Main Components

#### 1. **OpenAI Client Configuration**
```python
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```
- Uses Gemini API with OpenAI-compatible interface
- Requires `GEMINI_API_KEY` environment variable
- Enforces JSON response format for structured output

#### 2. **Available Tools**

The agent has access to 4 built-in tools:

##### **`get_weather(city: str)`**
- Fetches current weather for a specified city
- Uses wttr.in API
- Returns formatted weather string (condition + temperature)
- Example: `"The weather in London is Partly cloudy +12°C"`

##### **`run_command(cmd: str)`**
- Executes shell commands with **whitelisted safety restrictions**
- Allowed commands: `ls`, `pwd`, `mkdir`, `touch`, `cat`, `tree`, `cd`, `rm`
- Features:
  - 10-second timeout to prevent hanging
  - Captures stdout/stderr
  - Returns clear error messages for unauthorized commands
- Use case: Create directories, navigate, list files

##### **`write_file(filepath: str, content: str)`**
- Creates or overwrites files with specified content
- Auto-creates parent directories if they don't exist
- Supports any text-based format (HTML, Python, JSON, etc.)
- Returns confirmation with character count
- Input format from agent: `"filepath|||content"` (triple-pipe delimiter)

##### **`read_file(filepath: str)`**
- Reads and returns file content
- Handles errors gracefully (file not found, read errors)
- Returns full file path + content for context

#### 3. **System Prompt (Agent Instructions)**

The system prompt defines:
- **Agent Personality**: Helpful AI Assistant
- **Operating Mode**: Plan → Action → Observe cycle
- **Output Format**: Strict JSON structure
- **Tool Descriptions**: Details about each available tool
- **Example Workflow**: Step-by-step demonstration

### JSON Response Format

The agent responds in this structured format:

```json
{
    "step": "plan|action|output|observe",
    "content": "Human-readable explanation",
    "function": "tool_name (only for action steps)",
    "input": "parameter for the tool"
}
```

**Step Types:**
- **`plan`**: Agent thinks through the problem
- **`action`**: Agent calls a tool with specific input
- **`observe`**: System reports tool execution results (internal)
- **`output`**: Agent provides final answer to user

---

## 🎯 Step-by-Step Execution Flow

### Example: "Create a Python script that prints hello world"

1. **User Input**
   ```
   > create a python script that prints hello world
   ```

2. **Agent Plans**
   ```json
   { "step": "plan", "content": "I need to create a Python file with a hello world program" }
   ```
   Output: `🧠: I need to create a Python file with a hello world program`

3. **Agent Acts (Tool Call)**
   ```json
   { "step": "action", "function": "write_file", "input": "hello.py|||print('Hello World')" }
   ```
   Output: `🛠️: Calling write_file('hello.py|||print('Hello World')`

4. **System Executes Tool**
   - File is created with content
   - Success message returned
   ```
   ✅: Successfully created file: hello.py (21 characters)
   ```

5. **Agent Provides Final Answer**
   ```json
   { "step": "output", "content": "Successfully created hello.py with hello world program" }
   ```
   Output: `🤖: Successfully created hello.py with hello world program`

---

## 💻 Main Code Structure

### Message Management
```python
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
```
- Maintains conversation history
- System message defines agent behavior
- User queries and assistant responses are appended
- Enables multi-turn conversations with context

### Main Loop
```python
while True:
    query = input("> ")  # Get user input
    messages.append({"role": "user", "content": query})
    
    while True:  # Inner loop for agent iterations
        # Call Gemini API
        response = client.chat.completions.create(...)
        
        # Parse and handle JSON response
        # Process plan/action/output steps
        # Execute tools as needed
```

### Response Handling (Fixed Multi-Step Support)

The code handles both response patterns:
- **Single object**: `{ "step": "plan", ... }`
- **Array of steps**: `[ { "step": "plan", ... }, { "step": "action", ... } ]`

**Key Processing:**
1. Parse JSON response
2. Convert to list of steps (single object → list wrapper)
3. Iterate through each step
4. Execute actions and collect results
5. Break on final output or error

### Tool Execution Logic

```python
if tool_name in available_tools:
    if tool_name == "write_file":
        # Parse special format: filepath|||content
        parts = tool_input_str.split("|||", 1)
        filepath, content = parts[0], parts[1]
        output = available_tools[tool_name](filepath, content)
    else:
        # Other tools: direct call
        output = available_tools[tool_name](tool_input_str)
    
    # Send result back to agent as observation
    messages.append({"role": "user", "content": json.dumps({...})})
```

---

## 🚀 Usage

### Setup

1. **Install Dependencies**
   ```bash
   pip install openai python-dotenv requests
   ```

2. **Environment Configuration**
   Create `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Running the Agent

```bash
python cli/main.py
```

Output:
```
🤖 Agent ready! Type your query or 'exit' to quit.

>
```

### Example Commands

```
# Weather query
> What's the weather in Paris?

# Create files
> Create an HTML file called index.html with a basic structure

# File operations
> Read the contents of hello.py

# Complex tasks
> Make a streamlit app for analyzing student marks

# Exit
> exit
```

---

## 🔧 Configuration & Customization

### Debug Mode
```python
DEBUG = True  # Set to False to hide API responses
```
- Shows raw JSON responses from Gemini API
- Useful for debugging agent behavior

### Safe Commands Whitelist
```python
safe_commands = ['ls', 'pwd', 'mkdir', 'touch', 'cat', 'tree', 'cd', 'rm']
```
- Located in `run_command()` function
- Add new commands carefully for security

### API Model
```python
model="gemini-3-flash-preview"  # Can be changed to other Gemini models
```

### Timeout Settings
```python
timeout=10  # 10-second limit for command execution
```

---

## 🐛 Error Handling

The system handles various error scenarios:

| Error | Handling |
|-------|----------|
| **Invalid JSON** | Catches `JSONDecodeError`, shows response, breaks loop |
| **Unknown Step Type** | Prints warning, continues processing |
| **Tool Not Found** | Returns error message, agent can retry |
| **File Operations** | Detailed error messages with context |
| **Command Timeout** | Returns timeout error after 10 seconds |
| **API Errors** | Caught in outer exception handler |
| **Keyboard Interrupt** | Graceful shutdown with goodbye message |

---

## 📊 Example Workflow: Student Marks Analysis Dashboard

**User Query:**
```
make a streamlit app for analysing student marks in subject of python, 
web-t, maths, dsa, coa use good graphs, barplot, and create custom 
dataset having roleno in format of 24cp401 to 24cp431 division 12 and 
24cp001-24cp020 are from div-3
```

**Agent Flow:**
1. **Plan**: "I will create a Python script to generate the custom dataset as a CSV file, then create a Streamlit application"
2. **Action**: Write `generate_data.py` to create student marks dataset
3. **Observe**: File created successfully
4. **Action**: Write `app.py` with Streamlit dashboard
5. **Observe**: File created successfully
6. **Output**: "Created dashboard with interactive graphs and analysis"

**Result**: Two Python files created ready for running Streamlit app

---

## 🔐 Security Considerations

1. **Command Whitelist**: Only safe, non-destructive commands are allowed
2. **Input Validation**: All user inputs are processed safely
3. **API Key**: Stored in environment variables, not hardcoded
4. **Error Isolation**: Exceptions don't crash the entire application
5. **Timeout Protection**: Commands that hang are automatically terminated

---

## 📝 Tips & Best Practices

### For Better Results:
1. **Be specific** in queries: "Create an HTML form for user registration" works better than "make a form"
2. **Break complex tasks** into smaller steps if the agent struggles
3. **Provide context**: "Create a Python script that reads a CSV file and prints statistics"
4. **Check the DEBUG output** if something goes wrong

### Known Limitations:
- Python execution is limited (no direct `python` command in whitelist)
- Commands must be in the safe whitelist
- Single-turn file creation is easier than complex multi-step debugging
- Large file content may hit API token limits

---

## 🎓 Learning Outcomes

This implementation demonstrates:
- **Agentic AI Pattern**: How LLMs can be orchestrated to solve problems
- **Tool Integration**: Extending AI capabilities with external functions
- **JSON Parsing**: Structured communication with language models
- **Error Handling**: Robust system design with graceful failures
- **Conversation State**: Managing multi-turn interactions

---

## 📚 Further Reading

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Gemini API Documentation](https://ai.google.dev/)
- [ReAct Pattern](https://arxiv.org/abs/2210.03629) (Reasoning + Acting)
- [Agent Design Patterns](https://github.com/langchain-ai/langchain)

---

## 📄 License

Part of the Python-GenAi Learning Repository

