from healthbot.domain.evidence import EvidenceSource
from healthbot.services.answer_composer import AnswerComposer


def test_answer_composer_adds_sources_and_disclaimer():
    composer = AnswerComposer()

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

    result = composer.compose(
        "Flu symptoms can include fever, cough, and fatigue.",
        sources=sources,
    )

    assert "Flu symptoms can include" in result
    assert "Sources reviewed:" in result
    assert "CDC Flu Symptoms" in result
    assert "general educational information" in result


def test_answer_composer_can_skip_disclaimer():
    composer = AnswerComposer()

    result = composer.compose(
        "Flu symptoms can include fever.",
        include_disclaimer=False,
    )

    assert "general educational information" not in result
