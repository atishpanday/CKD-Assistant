from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from utils.rag_chain import call_chain

import asyncio

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


def format_message(message: Message):
    if message.role == "user":
        return "human: " + message.content
    else:
        return "ai: " + message.content


@router.post("/chat")
async def respond_to_message(messages: list[Message]):
    num_messages = len(messages)
    question = messages[num_messages - 1].content
    chat_history = ""
    for m in messages[0:-1]:
        chat_history += "\n" + format_message(m)

    return StreamingResponse(
        call_chain(question, chat_history), media_type="application/json"
    )
