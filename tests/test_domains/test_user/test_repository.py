import pytest

from project.domains.base.exceptions import NotFoundError
from project.domains.user.repositories import UserRepository
from tests.factories import UserFactory


class TestUserRepository:
    def test_not_found_error_user(self, session):
        repo = UserRepository()
        with pytest.raises(NotFoundError):
            repo.get(0)

    def test_not_found_user(self, session):
        repo = UserRepository()
        assert not repo.get_or_none(0)

    def test_get_user(self, session):
        user = UserFactory()
        repo = UserRepository()

        assert repo.get_or_none(user.id).id == user.id

    def test_all_user(self, session):
        UserFactory()
        UserFactory()
        UserFactory()
        repo = UserRepository()
        result = repo.all()

        assert len(result) == 3

    def test_get_nonexistent_user(self, session):
        repo = UserRepository()
        assert repo.get_or_none(0) is None

    def test_new_user(self, session):
        repo = UserRepository()
        user_data = {"name": "Test User", "telegram_user_id": 1234, "telegram_username": "testuser", "is_admin": False}
        user = repo.new(**user_data)

        assert user.name == user_data["name"]
        assert user.telegram_user_id == user_data["telegram_user_id"]
        assert user.telegram_username == user_data["telegram_username"]
        assert user.is_admin == user_data["is_admin"]

    def test_create_user(self, session):
        repo = UserRepository()
        user_data = {"name": "Test User", "telegram_user_id": 12345, "telegram_username": "testuser", "is_admin": False}
        user = repo.create(**user_data)
        session.delete(user)

        assert user.id is not None
        assert user.name == user_data["name"]
        assert user.telegram_user_id == user_data["telegram_user_id"]
        assert user.telegram_username == user_data["telegram_username"]
        assert user.is_admin == user_data["is_admin"]

    def test_save_user(self, session):
        repo = UserRepository()
        user_data = {
            "name": "Test User",
            "telegram_user_id": 123456,
            "telegram_username": "testuser",
            "is_admin": False,
        }
        user = repo.new(**user_data)
        repo.save(user)

        saved_user = repo.get_or_none(user.id)
        session.delete(user)

        assert saved_user.id == user.id
        assert saved_user.name == user_data["name"]
        assert saved_user.telegram_user_id == user_data["telegram_user_id"]
        assert saved_user.telegram_username == user_data["telegram_username"]
        assert saved_user.is_admin == user_data["is_admin"]

    def test_update_fields(self, session):
        user = UserFactory()
        repo = UserRepository()
        updated_data = {"name": "Updated User", "telegram_username": "updateduser1"}
        repo.update_fields(user, **updated_data)
        session.delete(user)

        assert user.name == updated_data["name"]
        assert user.telegram_username == updated_data["telegram_username"]

    def test_update_and_save(self, session):
        repo = UserRepository()
        user = repo.create(name="Test User", telegram_user_id=0)
        updated_data = {"name": "Updated User", "telegram_username": "updateduser2"}
        repo.update_and_save(user, **updated_data)
        updated_user = repo.get_or_none(user.id)
        repo.delete_by_id(user.id)

        assert updated_user.name == updated_data["name"]
        assert updated_user.telegram_username == updated_data["telegram_username"]

    def test_delete_user(self, session):
        user = UserFactory()
        repo = UserRepository()

        repo.delete_by_id(user.id)

        assert repo.get_or_none(user.id) is None
