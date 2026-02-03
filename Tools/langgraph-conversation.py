"""
Tool Calling with LangChain
Shows how LangChain abstracts tool calling.
"""

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
import json
import math
import ast
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List 
from langgraph.graph.message import add_messages 
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# ============================================
# PART 1: Define Your Tools
# ============================================

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location"""
    # Simulated weather data
    weather_data = {
        "San Francisco": "Sunny, 72°F",
        "New York": "Cloudy, 55°F",
        "London": "Rainy, 48°F",
        "Tokyo": "Clear, 65°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")

@tool
#def calculator(input_json: str) -> str:
def calculator( operation: str, radius: float = None, width: float = None, length: float = None, height: float = None, expression: str = None, value: float = None ) -> str:
    """Compute calculations
    
    Supported operations:
    - "evaluate": evaluate a raw Python math expression (use 'expression')
    - "area_rectangle": the area of a rectangle 
    - "perimeter_rectangle": the perimeter of a rectangle
    - "volume_rectangle": the volume of a rectangle
    - "area_circle": the area of a circle
    - "circumference_circle": the circumference of a circle
    - "volume_sphere": the volume of a sphere
    - "sin": sine of a value (use 'value')
    - "cos": cosine of a value (use 'value')

    The 'operation' field must match one of the above exactly."""

    #data = json.loads(input_json)
    #op = data.get("operation")
    op = operation

    try:
        if op == "evaluate":
            expr = expression
            value = ast.literal_eval(expr)

        elif op == "area_rectangle":  
            w = width
            l = length
            value = w * l

        elif op == "perimeter_rectangle":  
            w = width
            l = length
            value = 2 * (w + l)

        elif op == "volume_rectangle":  
            w = width
            l = length
            h = height
            value = w * l * h

        elif op == "area_circle":  
            r = radius
            value = math.pi * (r ** 2)

        elif op == "circumference_circle":  
            r = radius
            value = math.pi * r * 2

        elif op == "volume_sphere":  
            r = radius
            value = (4 / 3) * math.pi * (r ** 3)

        elif op == "sin":
            x = value
            value = math.sin(x)

        elif op == "cos":
            x = value
            value = math.cos(x)

        else:
            return json.dumps({"error": f"Unknown operation '{op}'"})    
        return json.dumps({"result": value})
    except Exception as e:
        return json.dumps({"error": str(e)})
    
@tool
def count_letters(text: str, letter: str) -> str:
    """Count letter occurrences in a string. This tool is case-sensitive."""
    count = text.count(letter)
    return json.dumps({"count": count})


@tool
def compress_text(text: str) -> str:
    """Compress text by removing double letters: Hello --> Helo"""
    if not text:
        return json.dumps({"compressed": ""})
    
    compressed = [text[0]]
    for c in text[1:]:
        if c != compressed[-1]:
            compressed.append(c)

    return json.dumps({"compressed": "".join(compressed)})

# ============================================
# PART 2: Create LLM with Tools
# ===========================================
tools = [get_weather, calculator, count_letters, compress_text]
tool_map = {tool.name: tool for tool in tools}

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    should_exit: bool
    tool_count: int

# ============================================
# PART 3: The Agent Loop
# ============================================

def create_graph(llm):
    def get_user_input(state: AgentState) -> dict:
        print("\n" + "=" * 50)
        print("Enter your text (or 'quit' to exit):")
        print("=" * 50)

        print("\n> ", end="")
        user_input = input()
        print()

        # Check if user wants to exit
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            return {
                "messages": [HumanMessage(content=user_input)],
                "should_exit": True,        # Signal to exit the graph
                "tool_count": 0
            }
    
        return {
            "messages": [HumanMessage(content=user_input)],
            "should_exit": False,           # Signal to proceed to LLM
            "tool_count": 0
        }

    def call_llm(state: AgentState) -> dict:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}
    
    def call_tool(state: AgentState) -> dict:
        call_number = state.get("tool_count", 0) + 1
        print(f"\n🔧 Tool Call #{call_number}")

        last = state["messages"][-1]
        new_messages = []

        if hasattr(last, "tool_calls") and last.tool_calls:
            for tool_call in last.tool_calls:
                function_name = tool_call["name"]
                function_args = tool_call["args"]

                print(f"  Tool: {function_name}")
                print(f"  Args: {function_args}")
                
                # Execute the tool
                if function_name in tool_map:
                    result = tool_map[function_name].invoke(function_args)
                else:
                    result = f"Error: Unknown function {function_name}"
                
                print(f"  Result: {result}")

                new_messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tool_call["id"]
                ))

        return {"messages": new_messages, "tool_count": call_number}

    def print_response(state: AgentState) -> dict:
        response = state["messages"][-1]

        print("\n" + "-" * 50)
        print("LLM Response:")
        print("-" * 50)
        print(response.content)                                

        return {}

    def route_after_input(state: AgentState) -> str:
        if state.get("should_exit", False):
            return END
        
        last = state["messages"][-1]

        if not isinstance(last, HumanMessage):
            return "get_user_input"
        
        if last.content.strip() == "": 
            return "get_user_input"
        
        return "call_llm"

    def route_after_llm(state: AgentState) -> str:
        last = state["messages"][-1]

        if hasattr(last, "tool_calls") and last.tool_calls:
            return "call_tool"
        
        return "print_response"


    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("get_user_input", get_user_input)
    graph_builder.add_node("call_llm", call_llm)
    graph_builder.add_node("call_tool", call_tool)
    graph_builder.add_node("print_response", print_response)

    graph_builder.add_edge(START, "get_user_input")

    graph_builder.add_conditional_edges(
        "get_user_input",     
        route_after_input,     
        {
            "get_user_input": "get_user_input",
            "call_llm": "call_llm", 
            END: END         
        }
    )

    graph_builder.add_conditional_edges(
        "call_llm",
        route_after_llm,
        {
            "call_tool": "call_tool",
            "print_response": "print_response"
        }
    )

    graph_builder.add_edge("call_tool", "call_llm")
    graph_builder.add_edge("print_response", "get_user_input")

    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph

def save_graph_image(graph, filename="lg_graph.png"):
    """
    Generate a Mermaid diagram of the graph and save it as a PNG image.
    Uses the graph's built-in Mermaid export functionality.
    """
    try:
        #filename = os.path.join("graphs", filename)
        # Get the Mermaid PNG representation of the graph
        # This requires the 'grandalf' package for rendering
        png_data = graph.get_graph(xray=True).draw_mermaid_png()

        # Write the PNG data to file
        with open(filename, "wb") as f:
            f.write(png_data)

        print(f"Graph image saved to {filename}")
    except Exception as e:
        print(f"Could not save graph image: {e}")
        print("You may need to install additional dependencies: pip install grandalf")


# ============================================
# PART 4: Test It
# ============================================

def main():

    # Create LLM
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    print("=" * 50)
    print("LangGraph Agent with gpt-4o-mini")
    print("=" * 50)
    print()

    print("\nCreating LangGraph...")
    graph = create_graph(llm_with_tools)
    print("Graph created successfully!")

    print("\nSaving graph visualization...")
    save_graph_image(graph)

    initial_state: AgentState = {
        "messages": [SystemMessage(content="You are a helpful assistant. Use the provided tools when needed.")],
        "should_exit": False,
    }

    config = {"configurable": {"thread_id": "my-chat-session"}, "recursion_limit": 100}

    current_state = graph.get_state(config)
    
    if current_state.next:
        print(f"\n🔄 RESUMING from checkpoint...")
        graph.invoke(None, config=config)
    else:
        graph.invoke(initial_state, config=config)



if __name__ == "__main__":
    main()