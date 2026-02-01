"""
Manual Tool Calling Exercise
Students will see how tool calling works under the hood.
"""

import json
from openai import OpenAI
import math
import ast
from dotenv import load_dotenv
import os

# ============================================
# PART 1: Define Your Tools
# ============================================

def get_weather(location: str) -> str:
    """Get the current weather for a location"""
    # Simulated weather data
    weather_data = {
        "San Francisco": "Sunny, 72°F",
        "New York": "Cloudy, 55°F",
        "London": "Rainy, 48°F",
        "Tokyo": "Clear, 65°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")

def calculator(input_json: str) -> str:
    data = json.loads(input_json)
    op = data.get("operation")

    try:
        if op == "evaluate":
            expr = data["expression"]
            value = ast.literal_eval(expr)

        elif op == "area_rectangle":  
            w = data["width"]
            l = data["length"]
            value = w * l

        elif op == "perimeter_rectangle":  
            w = data["width"]
            l = data["length"]
            value = 2 * (w + l)

        elif op == "volume_rectangle":  
            w = data["width"]
            l = data["length"]
            h = data["height"]
            value = w * l * h

        elif op == "area_circle":  
            r = data["radius"]
            value = math.pi * (r ** 2)

        elif op == "circumference_circle":  
            r = data["radius"]
            value = math.pi * r * 2

        elif op == "volume_sphere":  
            r = data["radius"]
            value = (4 / 3) * math.pi * (r ** 3)

        else:
            return json.dumps({"error": f"Unkown operation '{op}'"})    
        return json.dumps({"result": value})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================
# PART 2: Describe Tools to the LLM
# ============================================

# This is the JSON schema that tells the LLM what tools exist
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. San Francisco"
                    }
                },
                "required": ["location"]
            }
        }
    },
    # TODO: Students will add a second tool here (e.g., calculator)
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform arithmetic or geometric calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "evaluate | area_rectangle | perimeter_rectangle | volume_rectangle | area_circle | circumference_circle | volume_sphere"
                    },
                    "expression": {"type": "string"},
                    "radius": {"type": "number"},
                    "width": {"type": "number"},
                    "length": {"type": "number"},
                    "height": {"type": "number"}
                },
                "required": ["operation"]
            }
        }
    }
]


# ============================================
# PART 3: The Agent Loop
# ============================================

def run_agent(user_query: str):
    """
    Simple agent that can use tools.
    Shows the manual loop that LangGraph automates.
    """

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Start conversation with user query
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the provided tools when needed."},
        {"role": "user", "content": user_query}
    ]
    
    print(f"User: {user_query}\n")
    
    # Agent loop - can iterate up to 5 times
    for iteration in range(5):
        print(f"--- Iteration {iteration + 1} ---")
        
        # Call the LLM
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,  # ← This tells the LLM what tools are available
            tool_choice="auto"  # Let the model decide whether to use tools
        )
        
        assistant_message = response.choices[0].message
        
        # Check if the LLM wants to call a tool
        if assistant_message.tool_calls:
            print(f"LLM wants to call {len(assistant_message.tool_calls)} tool(s)")
            
            # Add the assistant's response to messages
            messages.append(assistant_message)
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"  Tool: {function_name}")
                print(f"  Args: {function_args}")
                
                # THIS IS THE MANUAL DISPATCH
                # In a real system, you'd use a dictionary lookup
                if function_name == "get_weather":
                    result = get_weather(**function_args)
                elif function_name == "calculator":
                    result = calculator(json.dumps(function_args))
                else:
                    result = f"Error: Unknown function {function_name}"
                
                print(f"  Result: {result}")
                
                # Add the tool result back to the conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                })
            
            print()
            # Loop continues - LLM will see the tool results
            
        else:
            # No tool calls - LLM provided a final answer
            print(f"Assistant: {assistant_message.content}\n")
            return assistant_message.content
    
    return "Max iterations reached"


# ============================================
# PART 4: Test It
# ============================================

if __name__ == "__main__":
    # Test query that requires tool use
    print("="*60)
    print("TEST 1: Query requiring tool")
    print("="*60)
    run_agent("What's the weather like in San Francisco?")
    
    print("\n" + "="*60)
    print("TEST 2: Query not requiring tool")
    print("="*60)
    run_agent("Say hello!")
    
    print("\n" + "="*60)
    print("TEST 3: Multiple tool calls")
    print("="*60)
    run_agent("What's the weather in New York and London?")

    print("\n" + "="*60)
    print("TEST 4: Query requiring Calculator")
    print("="*60)
    run_agent("What's the area of a 2 by 4 rectangle?")

    print("\n" + "="*60)
    print("TEST 3: Multiple calculator calls")
    print("="*60)
    run_agent("What's the area and circumference of a circle with radius 5?")
