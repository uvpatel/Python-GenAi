from typing_extensions import TypedDict
from typing import Annotated

from langgraph.graph import StateGraph, START, END   # ✅ correct
from langgraph.graph.message import add_messages   
from langchain.chat_models import init_chat_model


from dotenv import load_dotenv

load_dotenv()


llm = init_chat_model(
    model="gemini-1.5-pro", 
    model_provider="google_genai"  
    )


class State(TypedDict):
    messages: Annotated[list,add_messages]
    

# defines nodes it just a function which does specific task
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    print("inside chatbot")
    return { "messages" : [response]}

print("\n")
def samplenode(state:State):
    print("inside samplenode")
    return { "messages" : ["Hi , this is a message from sample node"]}
print("\n")
    
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("samplenode",samplenode)

graph_builder.add_edge(START,"chatbot")

# start -> chatbot -> sample node -> end
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"messages": ["Hi, My name is Urvil Pate"]}))
print("\n")
print("\n")
print("updated_state",updated_state)



# state = { messages: ["Hey there"]}
# node runs: chatbot(state: State) -> { "messages" : ["Hi , this is a message from chatbot node"]} }
# state = { messages: ["Hey there", "Hi , this is a message from chatbot node"]} }