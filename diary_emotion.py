from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential  # Azure CLI 인증
from azure.ai.agents.models import ListSortOrder
import os
from dotenv import load_dotenv

load_dotenv()

# 1️⃣ Foundry 프로젝트에 연결 (Azure CLI 로그인 필요)
project_client = AIProjectClient(
    credential=AzureCliCredential(),
    endpoint=os.getenv('emotion_endpoint'),
    subscription_id=os.getenv('emotion_subscription_id'),
    resource_group_name=os.getenv('emotion_resource_group_name'),
    project_name=os.getenv('emotion_project_name')
)

# 2️⃣ 에이전트 및 새 스레드 생성
emotion_agent = project_client.agents.get_agent(os.getenv('emotion_agent'))
thread = project_client.agents.threads.create()

# 3️⃣ 유저 질문 처리 함수
def ask_agent(user_input):
    try:
        # 사용자 메시지 전송
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # 에이전트 실행
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=emotion_agent.id
        )

        if run.status == "failed":
            return {"error": f"실행 실패: {run.last_error}"}

        # 마지막 응답 메시지 가져오기
        messages = project_client.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )

        last_response_text = None
        for msg in reversed(list(messages)):
            if msg.role == "assistant" and msg.text_messages:
                last_response_text = msg.text_messages[-1].text.value
                break

        # 마지막 응답이 JSON 문자열일 경우 파싱
        import json
        try:
            response_json = json.loads(last_response_text)
            return response_json
        except json.JSONDecodeError:
            # JSON 파싱 실패시 그대로 문자열 반환
            return {"response": last_response_text or "⚠️ 응답이 비어 있습니다."}

    except Exception as e:
        return {"error": f"❗ 예외 발생: {str(e)}"}

user_input = """오늘은 학교에서 체육 시간이 있어서 너무 신났다! 줄넘기 시험을 봤는데, 내가 1분 동안 102번이나 넘었어. 선생님이 "정말 잘했어!"라고 칭찬해 주
        셔서 기분이 좋아졌다. 친구 민지랑은 조금 다퉜는데, 내가 실수로 그녀의 필통을 떨어뜨려서 화가 났다. 그래서 미안하다고 했더니 금방 화 풀고 같이 도시락도 먹었다. 
        엄마가 싸주신 김밥이 진짜 맛있어서 반 친구들도 한 개씩 나눠 먹었는데, 다들 맛있다고 해서 뿌듯했어. 집에 와서는 동생이랑 같이 애니메이션을 봤고, 강아지 
        토리가 내 무릎에 앉아서 같이 봤다. 오늘 하루는 기분 좋은 일도 있고, 속상한 일도 있었지만 전반적으로는 행복한 하루였던 것 같다!"""

if __name__ == "__main__":
    result = ask_agent(user_input)
    print("\n+++++++++++++최종 결과물+++++++++++++\n")
    print(result)