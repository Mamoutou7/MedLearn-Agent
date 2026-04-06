from healthbot.services.quiz_service import QuizApprovalService


def test_approve_true():
    service = QuizApprovalService()

    assert service.approve("approve") is True
    assert service.approve("APPROVE") is True
    assert service.approve(" approve ") is True


def test_approve_false():
    service = QuizApprovalService()

    assert service.approve("reject") is False
    assert service.approve("no") is False
    assert service.approve("") is False
