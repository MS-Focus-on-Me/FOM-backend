import requests
import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

def generate_mone_pastel_image(diary_text):

    nation = "대한민국"
    sex = "남"
    age = 26

    prompt = f"""
        {diary_text} 이 일기의 내용을 함축하는 그림을 한 장 그려줘.
        그림 스타일은 vivid하지 않은 파스텔톤으로, 그리고 초등학교 4학년의 그림체로 그려줘. 
        그림에는 어떠한 글자, 글씨, 문자도 나오지 않아야 해.
        다음은 나에 대한 기본적인 정보들이야. 이미지를 생성할 때 다음 정보들을 참고해. 단, 참고를 하는 것이지, 무조건적으로 내 정보들이 이미지에 드러나게 할 필요는 없어. 
        예를 들어, 내가 대한민국 사람이라고 해서 이미지에 무조건 태극기가 들어가야 할 필요는 없어.
        국적: {nation}
        성별: {sex}
        나이: {age}
        """

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
    diary_text = """오늘 하루는 정말 뜻깊고 소중한 시간이었어요. 아침 햇살이 창문을 통해 은은하게 들어오면서, 마음이 차분해지고 기분이 좋아졌어요. 잠깐 커피를 마시며 지난 일들을 되돌아보니, 작지만 소중한 순간들이 하나하나 떠올라 행복감이 밀려왔어요.  
오늘은 미루었던 일들을 하나씩 해결하는 성취감도 느꼈고, 친구들과의 작은 대화 속에서도 따뜻함을 느꼈어요. 오늘의 하루가 감장을 채우고 마음을 더욱 풍요롭게 만들어준 것 같아요. 내일은 오늘보다 더 웃고, 더 성장하는 하루가 되도록 다짐하며 하루를 마무리했어요. 내일도 기대와 희망을 품고 힘차게 시작할게요.  
이 작은 일기장이 오늘 하루를 기록하며, 내 마음속 소중한 기억들로 남기를 바랍니다. 내 마음에 새겨진 작은 행복들을 잊지 않고, 앞으로도 긍정적인 마음가짐으로 살아가야겠어요."""
    generate_mone_pastel_image(diary_text)