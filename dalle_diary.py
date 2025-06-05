import requests
import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()



def generate_mone_pastel_image(diary_text):

    nation = "대한민국"

    prompt = f"""{diary_text} 이 일기에 나오는 풍경 중 하나를 vivid하지 않은 파스텔톤의 초등학교 4학년 그림으로 그려줘. 그리고 글씨는 안 나오게 그림만 나오게 해줘. 
    나는 {nation} 국적이야. 이미지를 생성할 때는 내 국적과 문화권을 반영한 내용으로 생성해줘."""

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
    diary_text = "6월 5일 오늘은 현충일이라 차분하게 보냈습니다. 나라를 위해 헌신하신 분들께 감사하는 마음을 가졌습니다. 집에서 태극기를 게양하고 묵념을 했습니다. 숭고한 희생의 의미를 되새기는 시간이었습니다. 오후에는 조용히 책을 읽으며 사색하는 시간을 가졌습니다. 복잡한 생각들이 정리되고 마음이 차분해졌습니다. 저녁에는 가족들과 함께 역사 다큐멘터리를 시청하며 의미 있는 시간을 보냈습니다. 뜻깊은 하루였습니다."
    generate_mone_pastel_image(diary_text)