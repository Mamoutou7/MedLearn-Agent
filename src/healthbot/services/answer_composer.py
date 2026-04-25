from __future__ import annotations

from healthbot.domain.evidence import EvidenceSource
from healthbot.services.citation_formatter import CitationFormatter


class AnswerComposer:
    """Builds final user-facing answers from content,
    safety notes, and evidence.
    """

    EDUCATIONAL_DISCLAIMER = "This is general educational information \
        and is not a diagnosis. For personal medical advice, please consult \
        a qualified healthcare professional."

    def __init__(self, citation_formatter: CitationFormatter | None = None) -> None:
        self.citation_formatter = citation_formatter or CitationFormatter()

    def compose(
        self,
        answer: str,
        *,
        sources: list[EvidenceSource] | None = None,
        include_disclaimer: bool = True,
    ) -> str:
        parts = [answer.strip()]

        if sources:
            citations = self.citation_formatter.format_sources(sources)
            if citations:
                parts.append(citations)

        if include_disclaimer:
            parts.append(self.EDUCATIONAL_DISCLAIMER)

        return "\n\n".join(part for part in parts if part)
