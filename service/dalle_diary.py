import requests
import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

def generate_mone_pastel_image(diary_text, nation, sex, age):

    nation = nation
    sex = sex
    age = age

    prompt = f"""
            참고 내용:
            {diary_text}

            위의 일기 내용을 바탕으로, 하루의 분위기와 감정을 표현한 그림을 그려주세요.
            그림은 **모네의 화풍**(인상주의 스타일)과 **부드러운 파스텔톤 색감**을 기반으로 하며,
            텍스트나 문자는 **절대 포함하지 않습니다**.

            이미지는 일기의 분위기와 정서를 시각적으로 전달하는 데 집중해주세요.
            사용자의 정보를 참고해 문화적 맥락이나 정서적 분위기를 간접적으로 반영할 수 있습니다.
            국적, 성별, 나이 등은 반드시 드러날 필요는 없지만, 내용에 어울린다면 자연스럽게 반영될 수 있습니다.

            참고용 사용자 정보:
            - 국적: {nation}
            - 성별: {sex}
            - 나이: {age}
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