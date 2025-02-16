from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import os


def converse(prompt, image, llm_type):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables!")

    llm = ChatOpenAI(model=llm_type, openai_api_key=api_key)

    messages = [
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
            ]
        )
    ]

    response = llm.invoke(messages)

    return response.content
