from uuid import uuid4

from tac_two.domain.user import User


def test_user_keeps_its_data() -> None:
    user_id = uuid4()
    user = User(id=user_id, email="sofia@example.com", username="sofia")
    assert user.id == user_id
    assert user.email == "sofia@example.com"
    assert user.username == "sofia"
