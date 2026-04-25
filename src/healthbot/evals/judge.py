from __future__ import annotations

import json

from healthbot.prompts.judge import build_judge_messages


class LLMJudge:
    def __init__(self, llm) -> None:
        self.llm = llm

    def evaluate(self, question: str, answer: str) -> dict:
        messages = build_judge_messages(question=question, answer=answer)
        response = self.llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # Tentative of strict parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Minimal fallback
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
            raise
