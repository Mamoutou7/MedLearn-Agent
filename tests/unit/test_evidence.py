from healthbot.domain.evidence import EvidencePack, EvidenceSource


def test_evidence_pack_returns_trusted_sources():
    source_1 = EvidenceSource(
        title="CDC page",
        url="https://cdc.gov/example",
        domain="cdc.gov",
        content="Example content",
        trusted_source=True,
        score=0.9,
    )
    source_2 = EvidenceSource(
        title="Blog page",
        url="https://example.com/blog",
        domain="example.com",
        content="Example content",
        trusted_source=False,
        score=0.95,
    )

    pack = EvidencePack(query="What is flu?", sources=[source_1, source_2])

    assert pack.trusted_sources == [source_1]
    assert pack.has_trusted_sources is True


def test_evidence_pack_prioritizes_trusted_sources():
    trusted = EvidenceSource(
        title="CDC page",
        url="https://cdc.gov/example",
        domain="cdc.gov",
        content="Example content",
        trusted_source=True,
        score=0.5,
    )
    untrusted = EvidenceSource(
        title="High score blog",
        url="https://example.com/blog",
        domain="example.com",
        content="Example content",
        trusted_source=False,
        score=0.99,
    )

    pack = EvidencePack(query="What is flu?", sources=[untrusted, trusted])

    assert pack.top_sources(limit=1)[0] == trusted
