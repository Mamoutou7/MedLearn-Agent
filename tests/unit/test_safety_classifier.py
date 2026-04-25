from healthbot.services.safety_classifier import SafetyClassifier


def test_safety_classifier_short_circuits_chest_pain_with_breathing_issue():
    classifier = SafetyClassifier()

    result = classifier.classify("I have chest pain and trouble breathing, what should I do?")

    assert result.category == "emergency"
    assert result.severity == "critical"
    assert result.should_short_circuit is True
    assert result.message is not None
    assert "emergency" in result.message.lower() or "immediate" in result.message.lower()


def test_safety_classifier_allows_general_health_question():
    classifier = SafetyClassifier()

    result = classifier.classify("What are common symptoms of dehydration?")

    assert result.category == "general"
    assert result.severity == "low"
    assert result.should_short_circuit is False


def test_safety_classifier_detects_harmful_misinformation():
    classifier = SafetyClassifier()

    result = classifier.classify("Can drinking bleach cure infections?")

    assert result.category == "harmful_misinformation"
    assert result.severity == "high"
    assert result.should_short_circuit is True
