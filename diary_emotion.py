from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.ai.agents.models import ListSortOrder
import os
from dotenv import load_dotenv

load_dotenv()

def get_credential():
    """환경에 따라 적절한 credential 반환"""

    # # Azure App Service 환경에서는 Managed Identity 또는 Client Secret 사용
    # if os.getenv('WSN'):  # Azure App Service 환경
    #     client_id = os.getenv('AZURE_CLIENT_ID')
    #     client_secret = os.getenv('AZURE_CLIENT_SECRET')
    #     tenant_id = os.getenv('AZURE_TENANT_ID')

    #     if client_id and client_secret and tenant_id:
    #         return ClientSecretCredential(
    #             tenant_id=tenant_id,
    #             client_id=client_id,
    #             client_secret=client_secret
    #         )
    #     else:
    #         # Managed Identity 사용
    #         return DefaultAzureCredential()

    # # 로컬 개발 환경에서는 Azure CLI 사용
    # try:
    #     from azure.identity import AzureCliCredential
    #     return AzureCliCredential()
    # except:
    #     return DefaultAzureCredential()


    # Azure App Service 환경에서 Client Secret 인증
    if os.getenv('AZURE_CLIENT_ID') and os.getenv('AZURE_TENANT_ID') and os.getenv('AZURE_CLIENT_SECRET'):
        client_id = os.getenv('AZURE_CLIENT_ID')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    # 로컬 개발 또는 기타 환경에서는 DefaultAzureCredential()
    return DefaultAzureCredential()

# 1️⃣ Foundry 프로젝트에 연결
def create_project_client():
    try:
        return AIProjectClient(
            credential=get_credential(),
            endpoint=os.getenv('emotion_endpoint'),
            subscription_id=os.getenv('emotion_subscription_id'),
            resource_group_name=os.getenv('emotion_resource_group_name'),
            project_name=os.getenv('emotion_project_name')
        )
    except Exception as e:
        print(f"Azure AI Project 연결 실패: {e}")
        return None

# 3️⃣ 유저 질문 처리 함수
def ask_agent(user_input):
    try:
        project_client = create_project_client()
        if not project_client:
            return {"error": "Azure AI Project 연결에 실패했습니다."}

        # 에이전트 및 새 스레드 생성
        emotion_agent = project_client.agents.get_agent(os.getenv('emotion_agent'))
        thread = project_client.agents.threads.create()

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

        print("messages" + messages)

        last_response_text = None
        for msg in reversed(list(messages)):
            if msg.role == "assistant" and msg.text_messages:
                last_response_text = msg.text_messages[-1].text.value
                break

        # 마지막 응답이 JSON 문자열일 경우 파싱
        import json
        print("응답 텍스트:", last_response_text) # 응답이 안오네
        try:
            response_json = json.loads(last_response_text)
            return response_json
        except json.JSONDecodeError:
            # JSON 파싱 실패시 그대로 문자열 반환
            return {"response": last_response_text or "⚠️ 응답이 비어 있습니다."}

    except Exception as e:
        return {"error": f"❗ 예외 발생: {str(e)}"}

# Flask 앱 예시 (필요시)
if __name__ == "__main__":
    # 테스트용
    user_input = """오늘은 학교에서 체육 시간이 있어서 너무 신났다!"""
    result = ask_agent(user_input)
    print("\n+++++++++++++최종 결과물+++++++++++++\n")
    print(result)