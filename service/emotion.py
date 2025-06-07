import requests
import os
from dotenv import load_dotenv

load_dotenv()

def request_gpt(text):
    emotion_endpoint = os.getenv("emotion_agent_endpoint")
    # method = post
    
    headers = {
        "Content-Type": "application/json"
    }
    
    body = {
        "text": text
    }

    response=requests.post(emotion_endpoint,headers=headers,json=body) # response의 내용 파싱해서 사용
    print(response.status_code, response.reason)
    response_json = response.json()
    return response_json

if __name__ == "__main__":
    text = "오늘은 즐거운 일이 많았어"
    result = request_gpt(text)
    print(result)