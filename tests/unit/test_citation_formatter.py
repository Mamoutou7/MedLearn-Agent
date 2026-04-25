from healthbot.domain.evidence import EvidenceSource
from healthbot.services.citation_formatter import CitationFormatter


def test_citation_formatter_formats_sources():
    formatter = CitationFormatter()
    sources = [
        EvidenceSource(
            title="CDC Flu Symptoms",
            url="https://cdc.gov/flu/symptoms",
            domain="cdc.gov",
            content="Flu symptoms include fever and cough.",
            trusted_source=True,
            score=0.9,
        )
    ]

    result = formatter.format_sources(sources)

    assert "Sources reviewed:" in result
    assert "[1] CDC Flu Symptoms" in result
    assert "cdc.gov" in result
    assert "https://cdc.gov/flu/symptoms" in result


def test_citation_formatter_returns_empty_string_without_sources():
    formatter = CitationFormatter()

    assert formatter.format_sources([]) == ""
