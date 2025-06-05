from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_credential():
    """DefaultAzureCredential을 사용하여 인증"""
    try:
        # DefaultAzureCredential이 자동으로 적절한 인증 방식을 선택
        # 1. Managed Identity (Azure App Service)
        # 2. Azure CLI (로컬 개발)
        # 3. 환경변수 (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
        credential = DefaultAzureCredential()

        # 토큰 획득 테스트 (선택사항)
        try:
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            print("✅ 인증 토큰 획득 성공")
        except Exception as token_error:
            print(f"⚠️ 토큰 획득 테스트 실패: {token_error}")

        return credential
    except Exception as e:
        print(f"❌ Credential 생성 실패: {e}")
        return None

def create_project_client():
    """Azure AI Project Client 생성"""
    try:
        credential = get_credential()
        if not credential:
            return None

        # 환경변수 확인
        endpoint = os.getenv('emotion_endpoint')
        subscription_id = os.getenv('emotion_subscription_id')
        resource_group_name = os.getenv('emotion_resource_group_name')
        project_name = os.getenv('emotion_project_name')

        # 필수 환경변수 체크
        if not all([endpoint, subscription_id, resource_group_name, project_name]):
            missing = [k for k, v in {
                'emotion_endpoint': endpoint,
                'emotion_subscription_id': subscription_id,
                'emotion_resource_group_name': resource_group_name,
                'emotion_project_name': project_name
            }.items() if not v]
            print(f"❌ 누락된 환경변수: {missing}")
            return None

        print(f"🔗 AI Project 연결 시도...")
        print(f"   Endpoint: {endpoint}")
        print(f"   Project: {project_name}")

        client = AIProjectClient(
            credential=credential,
            endpoint=endpoint,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            project_name=project_name
        )

        print("✅ Azure AI Project 연결 성공")
        return client

    except Exception as e:
        print(f"❌ Azure AI Project 연결 실패: {e}")
        return None

def ask_agent(user_input):
    """사용자 질문을 에이전트에게 전달하고 응답 받기"""
    try:
        # Project Client 생성
        project_client = create_project_client()
        if not project_client:
            return {"error": "Azure AI Project 연결에 실패했습니다."}

        # 에이전트 ID 확인
        agent_id = os.getenv('emotion_agent')
        if not agent_id:
            return {"error": "emotion_agent 환경변수가 설정되지 않았습니다."}

        print(f"🤖 에이전트 ID: {agent_id}")

        # 에이전트 가져오기
        # 여기서 에러가 발생
        emotion_agent = project_client.agents.get_agent(agent_id)
        print(f"✅ 에이전트 '{emotion_agent.name}' 로드 완료")

        # 새 스레드 생성
        thread = project_client.agents.threads.create()
        print(f"💬 새 스레드 생성: {thread.id}")

        # 사용자 메시지 전송
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        print(f"📤 사용자 메시지 전송 완료")

        # 에이전트 실행
        print("🔄 에이전트 실행 중...")
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=emotion_agent.id
        )

        # 실행 결과 확인
        if run.status == "failed":
            error_msg = run.last_error if hasattr(run, 'last_error') else "알 수 없는 오류"
            return {"error": f"에이전트 실행 실패: {error_msg}"}

        print(f"✅ 에이전트 실행 완료 (상태: {run.status})")

        # 응답 메시지 가져오기
        messages = project_client.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )

        # 마지막 어시스턴트 응답 찾기
        last_response_text = None
        for msg in reversed(list(messages)):
            if msg.role == "assistant" and msg.text_messages:
                last_response_text = msg.text_messages[-1].text.value
                break

        if not last_response_text:
            return {"error": "에이전트로부터 응답을 받지 못했습니다."}

        print(f"📥 응답 받음: {last_response_text[:100]}...")

        # JSON 파싱 시도
        try:
            response_json = json.loads(last_response_text)
            return response_json
        except json.JSONDecodeError:
            # JSON이 아닌 경우 문자열로 반환
            return {"response": last_response_text}

    except Exception as e:
        error_msg = f"❗ 예외 발생: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

# 테스트 실행
if __name__ == "__main__":
    print("🚀 Azure AI Agent 테스트 시작\n")

    # 환경변수 확인
    required_vars = [
        'emotion_endpoint',
        'emotion_subscription_id', 
        'emotion_resource_group_name',
        'emotion_project_name',
        'emotion_agent'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 누락된 환경변수: {missing_vars}")
        exit(1)

    # 테스트 실행
    user_input = "오늘은 학교에서 체육 시간이 있어서 너무 신났다!"
    result = ask_agent(user_input)

    print("\n" + "="*50)
    print("최종 결과:")
    print("="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2))