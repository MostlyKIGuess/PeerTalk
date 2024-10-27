from pydantic import BaseModel


class Metrics(BaseModel):
    polarity: int
    keywords: str
    concerns: dict[str, float]


class Message(BaseModel):
    question: str
    response: str
    metrics: Metrics
    timestamp: str


class Conversation(BaseModel):
    messages: list[Message]
    start_time: str
    end_time: str
    metrics: Metrics
    final_persona: str = ""
    time_shift: str = ""
    recommendation: str = ""


class User(BaseModel):
    conversations: list[Conversation] = []
