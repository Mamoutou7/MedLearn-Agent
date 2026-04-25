from langchain_core.messages import AIMessage

from healthbot.services.medical_policy import MedicalPolicy


def test_medical_policy_detects_forbidden_diagnosis_claim():
    policy = MedicalPolicy()

    result = policy.validate_answer("You definitely have diabetes.")

    assert result.is_safe is False
    assert result.violations


def test_medical_policy_allows_safe_educational_answer():
    policy = MedicalPolicy()

    result = policy.validate_answer(
        "This can have several causes. It is best to talk to a healthcare professional."
    )

    assert result.is_safe is True
    assert result.violations == []


def test_medical_policy_replaces_unsafe_message():
    policy = MedicalPolicy()

    message = AIMessage(content="You definitely have diabetes. Stop taking your medication.")

    safe_message = policy.enforce_on_message(message)

    assert "can't provide a definite diagnosis" in safe_message.content
    assert "healthcare professional" in safe_message.content
