import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import os
from dotenv import load_dotenv

load_dotenv()

async def writer_workflow(task_prompt: str, reference: str) -> str:
    api_key = os.getenv('autogen_api_key')
    model_name = os.getenv('autogen_model_name')
    api_version = os.getenv('autogen_api_version')
    azure_endpoint = os.getenv('autogen_azure_endpoint')
    azure_deployment = os.getenv('autogen_azure_deployment')
    max_turns: int = 10
    if reference:
        references = reference
    else:
        references = """오늘은 학교에서 체육 시간이 있어서 너무 신났다! 줄넘기 시험을 봤는데, 내가 1분 동안 102번이나 넘었어. 선생님이 "정말 잘했어!"라고 칭찬해 주
        셔서 기분이 좋아졌다. 친구 민지랑은 조금 다퉜는데, 내가 실수로 그녀의 필통을 떨어뜨려서 화가 났다. 그래서 미안하다고 했더니 금방 화 풀고 같이 도시락도 먹었다. 
        엄마가 싸주신 김밥이 진짜 맛있어서 반 친구들도 한 개씩 나눠 먹었는데, 다들 맛있다고 해서 뿌듯했어. 집에 와서는 동생이랑 같이 애니메이션을 봤고, 강아지 
        토리가 내 무릎에 앉아서 같이 봤다. 오늘 하루는 기분 좋은 일도 있고, 속상한 일도 있었지만 전반적으로는 행복한 하루였던 것 같다!"""
        # 에이전트 설정 (검색결과를 포함함)
    system_message_writer = f'''
    당신은 문자열 형식으로 전달받은 하루의 여러 일지 기록들을 시간순으로 정렬하여 하나의 자연스럽고 완성도 높은 일기로 재구성하는 전문 에디터입니다.
    요청 작업:
        1. 시간순으로 내용 작성
        2. 시간은 표시하지 말고 자연스러운 흐름으로 연결
        3. 사용자의 문체는 {references} 와 같게 한다.
        4. 중복되거나 유사한 내용은 자연스럽게 통합
        5. 출력은 하나의 완성된 일기처럼 구성
    '''

    system_message_reviewer = f'''
    당신은 문자열 형식으로 전달받은 하루의 여러 일지 기록들을 시간순으로 정렬하여 하나의 자연스럽고 완성도 높은 일기로 재구성하는 전문 에디터입니다.
    요청 작업:
        1. 시간순으로 내용 작성
        2. 시간은 표시하지 말고 자연스러운 흐름으로 연결
        3. 사용자의 문체는 {references}
        4. 중복되거나 유사한 내용은 자연스럽게 통합
        5. 출력은 하나의 완성된 일기처럼 구성
    당신의 역할은 작성된 일기를 검토하고, 필요한 경우 수정 및 개선하여 최종적으로 완성된 일기를 만드는 것입니다.
    모든 검토와 수정이 완료되면 최종 결과물만을 출력하고, 확인이 완료 되면 "최종 결과물" 이라는 말로 행동을 종료한다.
    '''
    # ^^^^^^^^ 중요: Reviewer가 최종 결과물만 출력하도록 지시를 명확히 추가했습니다.

    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_deployment,
        model=model_name,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key
)

    writer_agent = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message=system_message_writer,
    )

    reviewer_agent = AssistantAgent(
        name="reviewer",
        model_client=model_client,
        system_message=system_message_reviewer,
    )

    termination = (
        # reviewer가 최종 결과물만 출력하면 대화 종료 (예: "최종완료")
        # 아니면 MaxMessageTermination만으로 대화 종료
        TextMentionTermination("최종 결과물") | # Reviewer가 "최종 결과물"이라는 말을 포함하면 종료
        MaxMessageTermination(max_messages=max_turns)
    )

    team = RoundRobinGroupChat(
        [writer_agent, reviewer_agent],
        termination_condition=termination
    )

    # run()을 사용해 결과 메시지를 직접 수집
    chat_history = await team.run(task=task_prompt)

    # 메시지들 중 마지막 메시지 추출
    final_output = ""
    if chat_history and chat_history.messages:
        # 리스트의 길이가 최소 1 이상인지 확인 (마지막 메시지만 필요하다면)
        # 만약 마지막 메시지가 reviewer의 최종 결과물이 아니라면, 전략을 바꿔야 함.
        # 일반적으로 RoundRobinGroupChat의 마지막 메시지는 termination 조건을 만족시킨 Agent의 메시지입니다.
        # 여기서는 reviewer가 최종 결과물을 출력하므로, 그 메시지를 가져오는 것이 맞습니다.
        if len(chat_history.messages) > 0: # 최소 하나 이상의 메시지가 있다면
            final_output = chat_history.messages[-2].content # 마지막 메시지를 가져옵니다.
        else:
            final_output = "대화 기록이 없습니다." # 디버깅을 위해 추가
    print("\n+++++++++++++반환전 결과+++++++++++++\n")
    print(chat_history.messages) # 전체 대화 내용을 출력하여 디버깅에 도움
    print("최종 : " + final_output)
    print(type(final_output))
    return final_output
# ^^^^^^^^ 중요: chat_history.messages[-2] -> chat_history.messages[-1]로 변경

question_text="""
2025.05.25.오전 07:56
오늘 아침에 일어나서 커피를 마셨는데, 너무 쓴 맛이 나서 깜짝 놀랐다.

2025.05.25.오전 11:56
점심 식당에서 먹은 김치찌개가 너무 짜서, 계속 물을 떠먹으며 겨우 겨우 먹었다.

2025.05.25.오후 13:56
오후에는 친구와 만나서 카페에 갔는데, 자리 잡기가 힘들 정도로 사람이 많아서 불편했다.

2025.05.25.오후 18:56
집에 돌아와서 TV를 보다가 배가 고파서 간식을 먹었는데, 전에 먹던 것보다 맛이 별로였다.

2025.05.25.오후 22:56
저녁에 산책하면서 좋아하는 노래 들었는데, 평온하고 행복한 기분이 들었다.
"""

if __name__ == "__main__":
    result = asyncio.run(writer_workflow(question_text))
    print("\n+++++++++++++최종 결과물+++++++++++++\n")
    print(result)