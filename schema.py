from pydantic import BaseModel


class TypingMetrics(BaseModel):
    keystrokes: int
    backspaces: int
    typing_speed: float

class Metrics(BaseModel):
    polarity: int
    keywords: str
    concerns: dict[str, float]


class Message(BaseModel):
    question: str
    response: str
    metrics: Metrics
    timestamp: str
    typing_metrics: TypingMetrics


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
