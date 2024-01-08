import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema
from src.repository.contacts import get_contacts, get_contact, get_birthday_contacts, create_contact, update_contact, delete_contact


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(id=1, username="test_user", email="test", password="test", refresh_token="test")
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, name="test_name1", surname="test_surname1", email="test_email1", phone_number="1234567890", birthday="12.03.2000", description="test"),
                    Contact(id=2, name="test_name2", surname="test_surname2", email="test_email2", phone_number="2345678901", birthday="11.03.2000", description="test")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 2
        contacts = [Contact(id=1, name="test_name1", surname="test_surname1", email="test_email1", phone_number="1234567890", birthday="12.03.2000", description="test"),
                    Contact(id=2, name="test_name2", surname="test_surname2", email="test_email2", phone_number="2345678901", birthday="11.03.2000", description="test")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactSchema(name="test_name1", surname="surname1", email="test-email@mail.tt", phone_number="1234567890", birthday="2020-01-01", description="test")
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)

    async def test_update_contact(self):
        body = ContactSchema(name="test_name1", surname="surname1", email="test-email@mail.tt", phone_number="1234567890", birthday="2020-01-01", description="test")
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = Contact(id=1, name="test_name1", surname="surname1", email="test-email@mail.tt", phone_number="1234567890", birthday="2020-01-01", description="test")
        self.session.execute.return_value = mocked_contacts

        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)

    async def test_delete_contact(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = Contact(id=1, name="test_name1", surname="surname1",
                                                                  email="test-email@mail.tt", phone_number="1234567890",
                                                                  birthday="2020-01-01", description="test")
        self.session.execute.return_value = mocked_contacts
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)

    @unittest.skip("Not implemented yet")
    async def test_get_birthday_contacts(self):
        contacts = [Contact(id=1, name="test_name1", surname="test_surname1", email="test_email1", phone_number="1234567890", birthday="12.03.2000", description="test"),
                    Contact(id=2, name="test_name2", surname="test_surname2", email="test_email2", phone_number="2345678901", birthday="11.03.2000", description="test")]

        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthday_contacts(self.session, self.user)
        self.session.execute.assert_called_once()
        self.assertEqual(result, contacts)
