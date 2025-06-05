import requests
import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

diary_text = "오늘 점심에 햄버거를 먹었어"

def generate_mone_pastel_image(diary_text):

    prompt = f"{diary_text} 이 일기에 나오는 풍경 중 하나를 vivid하지 않은 파스텔톤의 모네 그림으로 그려줘. 그리고 글씨는 안 나오게 그림만 나오게 해줘."

    api_key = os.getenv("DALLE_API_KEY")
    endpoint = os.getenv("DALLE_ENDPOINT")
    deployment = os.getenv("DALLE_DEPLOYMENT")
    api_version = os.getenv("DALLE_API_VERSION")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "size": "1792x1024",
        "quality": "standard",
        "style": "natural",
        "n": 1
    }

    url = f"{endpoint}/openai/deployments/{deployment}/images/generations?api-version={api_version}"

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print("📦 응답 상태:", response.status_code)
    print("📨 응답 내용:")
    print(json.dumps(response.json(), indent=2))

    try:
        image_url = response.json()['data'][0]['url']
        print("🖼️ 이미지 URL:", image_url)

        filename = "generated_image.png"
        urllib.request.urlretrieve(image_url, filename)
        print(f"💾 이미지가 '{filename}'으로 저장되었습니다.")

        return image_url, filename

    except (KeyError, IndexError):
        print("⚠️ 이미지 생성 실패. 응답 내용을 확인해주세요.")


if __name__ == "__main__":

    diary_text = "오늘 점심에 햄버거를 먹었어"
    generate_mone_pastel_image(diary_text)