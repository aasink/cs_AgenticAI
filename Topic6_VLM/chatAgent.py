import ollama
import base64
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict
import os
import sqlite3

class AgentState(TypedDict):
    user_input: str
    should_exit: bool
    llm_response: str
    messages: list

def create_graph():

    def get_user_input(state: AgentState) -> dict:
        return {}   # tkinter bypasses this node
        
    def call_vlm(state: AgentState) -> dict:
        messages = state["messages"]

        #print("\nProcessing your input...")

        response = ollama.chat(
            model='llava',
            messages=state["messages"],
        )

        reply = response["message"]["content"] 

        return {"llm_response": reply, "messages": messages + [{"role": "assistant", "content": reply}]}

    def route_after_input(state: AgentState) -> str:
        if state.get("should_exit", False):
            return END

        if state.get("user_input") == "":
            return "get_user_input"
        else:
            return "call_vlm"

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("get_user_input", get_user_input)
    graph_builder.add_node("call_vlm", call_vlm)

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

    graph_builder.add_edge("call_vlm", END)

    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph

def save_graph_image(graph, filename="lg_graph.png"):
    try:
        png_data = graph.get_graph(xray=True).draw_mermaid_png()

        with open(filename, "wb") as f:
            f.write(png_data)

        #print(f"Graph image saved to {filename}")
    except Exception as e:
        print(f"Could not save graph image: {e}")
        print("You may need to install additional dependencies: pip install grandalf")

def send_message(graph, user_input: str, image_path: str, state: AgentState, config: dict) -> AgentState:
    """Called by app.py each turn. Attaches image to first message only."""
    new_message = {"role": "user", "content": user_input}
    if not state.get("messages"):
        new_message["images"] = [image_path]

    updated_state = {
        **state,
        "user_input": user_input,
        "should_exit": False,
        "messages": state.get("messages", []) + [new_message],
    }

    return graph.invoke(updated_state, config=config)