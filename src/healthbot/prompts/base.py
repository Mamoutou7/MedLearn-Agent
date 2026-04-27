from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate


@dataclass(slots=True)
class PromptSpec:
    name: str
    version: str
    template: ChatPromptTemplate
    description: str = ""
    owner: str = "ai"
    status: str = "active"

    def format_messages(self, **kwargs: Any) -> list[BaseMessage]:
        """
        Render the prompt into LangChain messages.
        """
        return list(self.template.format_messages(**kwargs))

    @property
    def full_name(self) -> str:
        return f"{self.name}:{self.version}"


def build_chat_prompt(messages: Iterable[tuple[str, str]]) -> ChatPromptTemplate:
    """
    Small factory to standardize ChatPromptTemplate creation.
    """
    return ChatPromptTemplate.from_messages(list(messages))
