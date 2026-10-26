import pytest
from pydantic import ValidationError

from tac_two.api.schemas import UserCreate


def test_user_create_accepts_a_valid_username() -> None:
    user = UserCreate(
        email="sofia@example.com", password="password123", username="sofia_s"
    )
    assert user.username == "sofia_s"


@pytest.mark.parametrize("username", ["ab", "sofia scardovi", "a" * 31, "sofia!"])
def test_user_create_rejects_a_bad_username(username: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="sofia@example.com", password="password123", username=username)
