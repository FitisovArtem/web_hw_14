from datetime import date, timedelta

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of rows to skip
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Ensure that the user is only able to get their own contacts
    :return: A single contact from the database
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def get_birthday_contacts(days: int, db: AsyncSession, user: User):
    """
    The get_birthday_contacts function returns a list of contacts that have birthdays within the next 'days' days.
        The function takes in three parameters:
            1) days - an integer representing the number of days to look ahead for birthdays.  For example, if you want to find all contacts with birthdays in the next week, pass 7 as this parameter.
            2) db - an AsyncSession object from SQLAlchemy's asyncio engine (see https://docs.sqlalchemy.org/en/13/dialects/asyncpg.html#asynchronous-execution).  This is used by

    :param days: int: Specify the number of days in which to search for birthdays
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts with birthdays in the next n days
    :doc-author: Trelent
    """
    dateFrom = date.today()
    dateTo = date.today() + timedelta(days=days)
    thisYear = dateFrom.year
    nextYear = dateFrom.year + 1
    stmt = select(Contact).filter(or_(func.to_date(func.concat(func.to_char(Contact.birthday, "DDMM"), thisYear),
                                                   "DDMMYYYY").between(dateFrom, dateTo),
                                      func.to_date(func.concat(func.to_char(Contact.birthday, "DDMM"), nextYear),
                                                   "DDMMYYYY").between(dateFrom, dateTo))).filter_by(user=user)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the data passed in by the user
    :param db: AsyncSession: Access the database
    :param user: User: Get the user from the database and use it to create a contact
    :return: The contact object that was created
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactSchema): A ContactSchema object containing all fields for a new Contact object.
            db (AsyncSession): An async session with an open transaction to use for querying and updating data in the database.  This is provided by FastAPI via Dependency Injection, so you don't need to worry about it!  Just make sure you include it as an argument in your function definition, and FastAPI will handle passing this parameter when calling your function!

    :param contact_id: int: Get the contact with that id from the database
    :param body: ContactSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the jwt token
    :return: The updated contact
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.description = body.description
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to delete
    :param db: AsyncSession: Pass in the database session
    :param user: User: Make sure that the user is only deleting contacts they have created
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_contacts_by_params(name: str | None, surname: str | None, email: str | None, db: AsyncSession, user: User):
    """
    The get_contacts_by_params function is used to get contacts by name, surname or email.
        Args:
            name (str): The contact's first name.
            surname (str): The contact's last name.
            email (str): The contact's e-mail address.

    :param name: str | None: Filter the contacts by name
    :param surname: str | None: Filter the contacts by surname
    :param email: str | None: Filter the contacts by email
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Check if the user is logged in
    :return: A list of dictionaries with the following structure:
    :doc-author: Trelent
    """
    if name is not None:
        stmt = select(Contact.id, Contact.name, Contact.surname, Contact.email, Contact.phone_number, Contact.birthday, Contact.description).filter_by(name=name)
    elif surname is not None:
        stmt = select(Contact.id, Contact.name, Contact.surname, Contact.email, Contact.phone_number, Contact.birthday, Contact.description).filter_by(surname=surname)
    elif email is not None:
        stmt = select(Contact.id, Contact.name, Contact.surname, Contact.email, Contact.phone_number, Contact.birthday, Contact.description).filter_by(email=email)
    else:
        pass
    contacts = await db.execute(stmt)
    return contacts
