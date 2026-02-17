import ollama
import base64

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
#from langchain_community.llms import HuggingFacePipeline
from langchain_huggingface import HuggingFacePipeline
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict
import os
import sqlite3

def get_device():
    if torch.cuda.is_available():
        print("Using CUDA (NVIDIA GPU) for inference")
        return "cuda"
    elif torch.backends.mps.is_available():
        print("Using MPS (Apple Silicon) for inference")
        return "mps"
    else:
        print("Using CPU for inference")
        return "cpu"
    
class AgentState(TypedDict):
    user_input: str
    should_exit: bool
    model: str
    llm_response: str
    messages: list

def create_graph():

    def get_user_input(state: AgentState) -> dict:

        print("\n" + "=" * 50)
        print("Enter your text (or 'quit' to exit):")
        print("=" * 50)

        print("\n> ", end="")
        user_input = input()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            return {
                "user_input": user_input,
                "should_exit": True      
            }

        else:
            return {
                "user_input": user_input,
                "should_exit": False,           
                "messages": state["messages"] + [{"role": "user", "content": "Human: " + user_input}]
            }
        
    def call_vlm(state: AgentState) -> dict:

        if state.get("verbose"): 
            print("[TRACE] Entering call_llama node") 

        user_input = state["user_input"]

        system_prompt = sys_prompt("llama")

        messages = state["messages"]
        prompt = messages_to_prompt(messages, system_prompt)

        print("\nProcessing your input...")

        response = llm1.invoke(prompt)
        full = response

        response = full.split("Assistant:")[-1].strip() 

        return {"llm_response": response, "messages": messages + [{"role": "assistant", "content": "Llama: " + response}]}

    def print_response(state: AgentState) -> dict:
        print("\n" + "-" * 50)
        print("VLM Response:")
        print("-" * 50)
        print(state["llm_response"])

        return {}

    def route_after_input(state: AgentState) -> str:
        if state.get("should_exit", False):
            return END

        if state.get("user_input") == "":
            return "get_user_input"
        else:
            return "llmNode"

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("get_user_input", get_user_input)
    graph_builder.add_node("call_vlm", call_vlm)
    graph_builder.add_node("print_response", print_response)

    graph_builder.add_edge(START, "get_user_input")
    graph_builder.add_conditional_edges(
        "get_user_input",      
        route_after_input,     
        {
            "get_user_input": "get_user_input",
            "call_vlm": "call_vlm", 
            END: END                  
        }
    )

    graph_builder.add_edge("call_vlm", "print_response")
    graph_builder.add_edge("print_response", "get_user_input")

    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph

def save_graph_image(graph, filename="lg_graph.png"):
    try:
        filename = os.path.join("graphs", filename)
        png_data = graph.get_graph(xray=True).draw_mermaid_png()

        with open(filename, "wb") as f:
            f.write(png_data)

        print(f"Graph image saved to {filename}")
    except Exception as e:
        print(f"Could not save graph image: {e}")
        print("You may need to install additional dependencies: pip install grandalf")




def main():
    print("=" * 50)
    print("LangGraph Simple Agent with Llama-3.2-1B-Instruct & Qwen2.5-1.5B-Instruct")
    print("=" * 50)
    print()

    model_id1 = "meta-llama/Llama-3.2-1B-Instruct"
    model_id2 = "Qwen/Qwen2.5-1.5B-Instruct"
    
    llm1 = create_llm(model_id1)

    print("\nCreating LangGraph...")
    graph = create_graph(llm1, llm2)
    print("Graph created successfully!")

    print("\nSaving graph visualization...")
    save_graph_image(graph)

    initial_state: AgentState = {
        "user_input": "",
        "should_exit": False,
        "model": "llama",
        "llm_response": "",
        "qwen_response": "",
        "verbose": False,
        "messages": []
    }

    config = {"configurable": {"thread_id": "my-chat-session"}}

    current_state = graph.get_state(config)
    
    if current_state.next:
        print(f"\n🔄 RESUMING from checkpoint...")
        graph.invoke(None, config=config)
    else:
        graph.invoke(initial_state, config=config)

if __name__ == "__main__":
    main()




response = ollama.chat(
    model='llava',
    messages=[{
        'role': 'user',
        'content': 'Describe this image in English.',
        'images': ['./photo.jpg']
    }]
)
print(response['message']['content'])

with open("photo.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# # #