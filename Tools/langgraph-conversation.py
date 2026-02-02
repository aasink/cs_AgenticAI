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
    """Count letter occurances in a string"""
    count = text.lower().count(letter.lower())
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
# ============================================

# Create LLM
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

# Bind tools to LLM
tools = [get_weather, calculator, count_letters, compress_text]
tool_map = {tool.name: tool for tool in tools}

llm_with_tools = llm.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    should_exit: bool

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

        # Check if user wants to exit
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            return {
                "messages": [HumanMessage(content=user_input)],
                "should_exit": True        # Signal to exit the graph
            }
    
        return {
            "messages": [HumanMessage(content=user_input)],
            "should_exit": False,           # Signal to proceed to LLM
        }

    def call_llm(state: AgentState) -> dict:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}
    
    def call_tool(state: AgentState) -> dict:
        # TODO: finish this 
        return {}

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
        # TODO: finish this
        return call_tool


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

    graph_builder.add_edge("print_response", "get_user_input")

    graph = graph_builder.compile()

    return graph



def run_agent(user_query: str):
    """
    Simple agent that can use tools.
    Shows the manual loop that LangGraph automates.
    """
    
    # Start conversation with user query
    messages = [
        SystemMessage(content="You are a helpful assistant. Use the provided tools when needed."),
        HumanMessage(content=user_query)
    ]
    
    print(f"User: {user_query}\n")
    
    # Agent loop - can iterate up to 5 times
    for iteration in range(5):
        print(f"--- Iteration {iteration + 1} ---")
        
        # Call the LLM
        response = llm_with_tools.invoke(messages)
        
        # Check if the LLM wants to call a tool
        if response.tool_calls:
            print(f"LLM wants to call {len(response.tool_calls)} tool(s)")
            
            # Add the assistant's response to messages
            messages.append(response)
            
            # Execute each tool call
            for tool_call in response.tool_calls:
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
                
                # Add the tool result back to the conversation
                messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tool_call["id"]
                ))
            
            print()
            # Loop continues - LLM will see the tool results
            
        else:
            # No tool calls - LLM provided a final answer
            print(f"Assistant: {response.content}\n")
            return response.content
    
    return "Max iterations reached"



def save_graph_image(graph, filename="lg_graph.png"):
    """
    Generate a Mermaid diagram of the graph and save it as a PNG image.
    Uses the graph's built-in Mermaid export functionality.
    """
    try:
        filename = os.path.join("graphs", filename)
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

if __name__ == "__main__":
    # Test query that requires tool use
    print("="*60)
    print("TEST 1: Query requiring calculator")
    print("="*60)
    run_agent("What's the volume of sphere with radius 3?")

    print("\n" + "="*60)
    print("TEST 2: Query requiring letter count")
    print("="*60)
    run_agent("How may s are in the phrase: 'Mississippi riverboats'?")

    print("\n" + "="*60)
    print("TEST 3: Query requiring text compress")
    print("="*60)
    run_agent("Compress the word ‘bookkeeper'.")

    print("\n" + "="*60)
    print("TEST 4: Query requiring text compress & count letter")
    print("="*60)
    run_agent("Compress 'Falling yellow leaves filled the trail.' and then count how many l are in the compressed version.")

    print("\n" + "="*60)
    print("TEST 5: Query requiring count letter & calculator")
    print("="*60)
    run_agent("Count the number of r in ‘Crimson rivers roar loudly’, then compute the sine of that number'.")

    print("\n" + "="*60)
    print("TEST 6: Query requiring all 3 tools")
    print("="*60)
    run_agent("Compress the phrase ‘Glittering lanterns illuminate quiet streets’, count the i in the compressed text, and compute the sine of that count.")

    print("\n" + "="*60)
    print("TEST 7: Query requiring all 3 tools w/ multiple tool calls")
    print("="*60)
    run_agent("Count the l in 'Wandering spirits still drift softly along the hollow cliffs', compress the phrase, count the f in the compressed version, "
              "and compute the area of a circle whose radius is the difference between those two counts.")

    print("\n" + "="*60)
    print("TEST 8: Query using sequential chaining to hit 5-turn limit")
    print("="*60)
    run_agent("“Compress ‘balloon decorations’. Count the letter o. Take the sine of that count. Then compress ‘committee hallway’. Count the letter m. "
              "Take the sine of that count. Compare the two sine values and identify the one that is larger. Take the sine of that larger value. "
              "Finally compute the volume of a rectangular box with width equal to that final sine value, length 3, and height 2. Then take that resulting value "
              "and find the circumference, area of a circle with that as the radius. Then take the cosine of that value .Then use that value to find the volume of a "
              "sphere with that radius.")