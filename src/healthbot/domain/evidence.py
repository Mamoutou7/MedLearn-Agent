from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EvidenceSource:
    """A normalized source used for grounded health answers."""

    title: str
    url: str
    domain: str
    content: str
    trusted_source: bool
    score: float | None = None


@dataclass(slots=True)
class EvidencePack:
    """A structured group of evidence sources for one query."""

    query: str
    sources: list[EvidenceSource]

    @property
    def trusted_sources(self) -> list[EvidenceSource]:
        return [source for source in self.sources if source.trusted_source]

    @property
    def has_trusted_sources(self) -> bool:
        return bool(self.trusted_sources)

    def top_sources(self, limit: int = 5, *, trusted_first: bool = True) -> list[EvidenceSource]:
        """Return top evidence sources, optionally prioritizing trusted domains."""
        sources = list(self.sources)

        if trusted_first:
            sources.sort(
                key=lambda source: (
                    source.trusted_source,
                    source.score if source.score is not None else 0.0,
                ),
                reverse=True,
            )
        else:
            sources.sort(
                key=lambda source: source.score if source.score is not None else 0.0,
                reverse=True,
            )

        return sources[:limit]
