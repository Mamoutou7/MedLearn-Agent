from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate


@dataclass(frozen=True)
class PromptSpec:
    """
    Immutable prompt definition.

    Attributes
    ----------
    name : str
        Stable prompt identifier.
    version : str
        Prompt version for observability and evolution tracking.
    template : ChatPromptTemplate
        LangChain prompt template.
    """

    name: str
    version: str
    template: ChatPromptTemplate

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