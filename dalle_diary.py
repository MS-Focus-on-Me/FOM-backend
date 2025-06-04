import requests
import json
import urllib.request

def generate_mone_pastel_image(prompt, style="natural", size="1792x1024", quality="standard"):
    # Azure 구성 정보 (시크릿은 환경변수로 하는 걸 추천)
    api_key = "1WlHG4vHW7j9bH9EXu6OapqEhhGf78NHP3tswT8csyFw4aOxbzhSJQQJ99BEACfhMk5XJ3w3AAAAACOGPJcE"
    endpoint = "https://team-fome-sweden.cognitiveservices.azure.com/"
    deployment = "dall-e-3"
    api_version = "2024-04-01-preview"

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "style": style,
        "n": 1
    }

    url = f"{endpoint}/openai/deployments/{deployment}/images/generations?api-version={api_version}"

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.text}")

    resp_json = response.json()
    image_url = resp_json['data'][0]['url']
    filename = "generated_image.png"
    urllib.request.urlretrieve(image_url, filename)
    return {
        "image_url": image_url,
        "file_name": filename
    }