import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserSchema
from src.entity.models import User
from src.repository.users import create_user, get_user_by_email, update_token, confirmed_email, update_avatar_url


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.mocked_users = MagicMock()
        self.session.execute.return_value = self.mocked_users

    async def test_create_user(self):
        self.user = UserSchema(username="test_user1", email="test-email2@mail.tt", password="Pass123")
        result = await create_user(self.user, self.session)
        self.assertEqual(result.username, self.user.username)
        self.assertEqual(result.email, self.user.email)
        self.assertEqual(result.password, self.user.password)

    async def test_get_user_by_email(self):
        self.email = "test-email2@mail.tt"

        users = [User(username="test_user1", email="test-email1@mail.tt", password="Pass123", confirmed=False),
                 User(username="test_user2", email="test-email2@mail.tt", password="Pass123", confirmed=False),
                 User(username="test_user3", email="test-email3@mail.tt", password="Pass123", confirmed=False)]
        self.mocked_users.scalar_one_or_none.return_value = self.email
        result = await get_user_by_email(self.email, self.session)
        self.assertEqual(result, users[1].email)

    async def test_update_token(self):
        self.token = "test_token"
        self.user = User(id=1, username="test_user1", email="test-email2@mail.tt", password="Pass123",
                         refresh_token="refresh_token", created_at="2022-01-01 00:00:00",
                         updated_at="2022-01-02 00:00:00", confirmed=True)
        result = await update_token(self.user, self.token, self.session)
        self.assertEqual(self.user.refresh_token, self.token)

    #
    async def test_confirmed_email(self):
        self.user = User(id=1, username="test_user2", email="test-email2@mail.tt", password="Pass123", refresh_token="test", confirmed=False)
        result = await confirmed_email(str(self.user.email), self.session)
        self.assertEqual(self.user.confirmed, False)

    async def test_update_avatar_url(self):
        avatar = 'https://test.com/test.png'
        self.user = User(id=1, username="test_user2", email="test-email2@mail.tt", password="Pass123", refresh_token="test")
        result = await update_avatar_url(self.user.email, avatar, self.session)
        self.assertEqual(result.avatar, avatar)
