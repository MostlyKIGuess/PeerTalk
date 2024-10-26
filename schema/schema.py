from pydantic import BaseModel


class Message(BaseModel):
    question: str
    response: str
    polarity: int
    keywords: list = []
    concerns: dict[str, float] = {}


class Conversation(BaseModel):
    messages: list[Message]
    start_time: str
    end_time: str
    polarity: int
    keywords: list = []
    concerns: dict[str, float] = {}


class User(BaseModel):
    persona: list[str] = []
    conversations: list[Conversation] = []