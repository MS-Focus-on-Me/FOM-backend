import requests
import os
from dotenv import load_dotenv

load_dotenv()

def request_anonymous(text):
    anonymous_endpoint = os.getenv("ANONYMOUS_ENDPOINT")
    # method = post
    
    headers = {
        "Content-Type": "application/json"
    }
    
    body = {
        "text": text
    }

    response=requests.post(anonymous_endpoint,headers=headers,json=body) # response의 내용 파싱해서 사용
    print(response.status_code, response.reason)
    response_json = response.json()
    return response_json

if __name__ == "__main__":
    text = "내 이름은 이준형이고 나는 삼성전자에 취업했다가 어제 짤렸어 개열받아서 소주 10병에 콩나물국밥 조졌다."
    result = request_anonymous(text)
    print(result)