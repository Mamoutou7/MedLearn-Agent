from __future__ import annotations

from healthbot.domain.evidence import EvidenceSource


class CitationFormatter:
    """Formats evidence sources into user-facing citations."""

    def format_sources(self, sources: list[EvidenceSource]) -> str:
        """Format sources as a readable citation block."""
        if not sources:
            return ""

        lines = ["Sources reviewed:"]
        for idx, source in enumerate(sources, start=1):
            title = source.title or "Untitled source"
            domain = source.domain or "unknown source"
            url = source.url or ""

            if url:
                lines.append(f"[{idx}] {title} — {domain} — {url}")
            else:
                lines.append(f"[{idx}] {title} — {domain}")

        return "\n".join(lines)

    def format_inline_context(self, sources: list[EvidenceSource]) -> str:
        """Format sources for LLM context injection."""
        if not sources:
            return ""

        blocks = []
        for idx, source in enumerate(sources, start=1):
            blocks.append(
                "\n".join(
                    [
                        f"[{idx}] {source.title}",
                        f"Domain: {source.domain}",
                        f"Trusted: {source.trusted_source}",
                        f"URL: {source.url}",
                        f"Content: {source.content}",
                    ]
                )
            )

        return "\n\n".join(blocks)
