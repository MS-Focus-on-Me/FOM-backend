import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import os
from dotenv import load_dotenv
# pip install git+https://github.com/microsoft/autogen.git openai azure-identity

load_dotenv()

async def summary_workflow(task_prompt: str) -> str:
    api_key = os.getenv('autogen_api_key')
    model_name = os.getenv('autogen_model_name')
    api_version = os.getenv('autogen_api_version')
    azure_endpoint = os.getenv('autogen_azure_endpoint')
    azure_deployment = os.getenv('autogen_azure_deployment')
    max_turns: int = 10

    system_message_summarizer = '''
    당신은 사용자 일기를 요약하는 요약 전문가입니다.
    요약 조건:
    1. 핵심 내용만 간결하게 요약
    2. 문체는 자연스럽고 감정 흐름은 유지
    '''

    system_message_summary_reviewer = '''
    당신은 요약된 일기를 검토하는 전문가입니다.
    검토 조건:
    1. 요약이 원문의 핵심을 잘 반영하고 있는지 확인
    2. 수정이 필요하면 수정한 결과만 출력 (그 외 설명 없이)
    '''

    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_deployment,
        model=model_name,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key
    )

    summary_agent = AssistantAgent(
    name="summary",
    model_client=model_client,
    system_message=system_message_summarizer,
    )

    summary_reviewer_agent = AssistantAgent(
        name="summary_reviewer",
        model_client=model_client,
        system_message=system_message_summary_reviewer,
    )


    termination = (
        # reviewer가 최종 결과물만 출력하면 대화 종료 (예: "최종완료")
        # 아니면 MaxMessageTermination만으로 대화 종료
        TextMentionTermination("최종 결과물") | # Reviewer가 "최종 결과물"이라는 말을 포함하면 종료
        MaxMessageTermination(max_messages=max_turns)
    )

    team = RoundRobinGroupChat(
        [summary_agent, summary_reviewer_agent],
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
    return final_output
# ^^^^^^^^ 중요: chat_history.messages[-2] -> chat_history.messages[-1]로 변경

question_text="""
025년 5월 25일  
아침에 일어나서 커피를 마셨는데, 평소보다 쓴 맛이 강해서 조금 놀랐다. 점심으로 식당에서 김치찌개를 먹었는데, 
짠 맛이 강해서 물을 자꾸 떠먹으며 겨우 다 먹을 수 있었다. 오후에는 친구랑 카페에 갔지만, 사람이 너무 많아 자리를 잡기가 쉽지 않아 조금 불편했다. 
저녁에는 집에서 TV를 보다가 배가 고파서 간식을 먹었는데, 익숙한 맛이 아니라서 살짝 아쉬웠다. 하지만 밤 산책을 하면서 좋아하는 
노래를 들으니 마음이 차분해지고 행복한 기분이 들었다. 오늘은 작은 불편한 일이 몇 가지 있었지만, 마지막에 산책하며 느낀 평온함 덕분에 잘 마무리된 하루였다.  
"""

if __name__ == "__main__":
    result = asyncio.run(summary_workflow(question_text))
    print("\n+++++++++++++최종 결과물+++++++++++++\n")
    print(result)