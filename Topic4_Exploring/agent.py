from youtube_transcript_api import YouTubeTranscriptApi
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
#from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import re
import json

@tool
def get_youtube_transcript(video_id: str) -> str:
    """Fetch the transcript of a YouTube video by video ID."""
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return " ".join([entry.text for entry in transcript.snippets])

@tool
def extract_video_id(url: str) -> str:
    """Extract a YouTube video ID from a URL or return the ID if already provided."""
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    
    match = re.search(r"v=([A-Za-z0-9_-]{11})", url)
    if match: return match.group(1)

    match = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", url)
    if match: return match.group(1)

    raise ValueError("Could not extract a valid YouTube video ID from the URL.")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Create agent with tool
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
agent = create_react_agent(llm, [get_youtube_transcript])

'''
# Test it
result = agent.invoke({
    "messages": [("user", "Get the transcript for video dQw4w9WgXcQ and summarize it")]
})

for i in result["messages"]:
    print(i.content)'''

def analyze_video(url: str): 
    prompt = f""" You will analyze a YouTube video. 
    
    Steps: 1. Call the tool `extract_video_id` using this URL: {url} 
    2. Call the tool `get_youtube_transcript` using the extracted video ID. 
    3. Using the transcript, produce: 
        - A concise summary 
        - A list of key concepts 
        - Five quiz questions Return the final answer as JSON with keys: summary, key_concepts, quiz_questions. 
    """ 
    
    result = agent.invoke({"messages": [("user", prompt)]}) 
    final_msg = result["messages"][-1].content
    return final_msg

def main():
    print("\nYoutube Video Transcript Analyzer") 
    print("Type 'exit' to quit.\n") 
    
    while True: 
        url = input("Enter a YouTube URL: ").strip() 
        
        if url.lower() == "exit": 
            print("Goodbye!") 
            break 
        
        try: 
            result = analyze_video(url)

            clean = result.strip()

            summary = clean.split('"summary":')[1].split('",')[0].strip().lstrip('"')

            key_concepts_block = clean.split('"key_concepts":')[1].split(']')[0]
            key_concepts = [item.strip().strip('"') for item in key_concepts_block.strip("[ ").split(",")]

            quiz_block = clean.split('"quiz_questions":')[1].split(']')[0]
            quiz_questions = [item.strip().strip('"') for item in quiz_block.strip("[ ").split(",")]

            print("\n\n=== Analysis Result ===") 
            print("\n=== Summary ===")
            print(summary)

            print("\n=== Key Concepts ===")
            for c in key_concepts:
                print(f"- {c}")

            print("\n=== Quiz Questions ===")
            for q in quiz_questions:
                print(f"- {q}")
            print(f"\n{'-' * 80}\n")

        except Exception as e: 
            print(f"\nError: {e}\n")

    
if __name__ == "__main__":
    main()

    #https://www.youtube.com/watch?v=XKSjCOKDtpk
    #https://www.youtube.com/watch?v=u-MH4sf5xkY
    #https://www.youtube.com/watch?v=ZJqY1WLX4zA