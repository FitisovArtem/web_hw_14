from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactResponse, ContactSchema
from src.services.auth import auth_service
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse], tags=['contacts'],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set the minimum value for a parameter
    :param le: Limit the maximum number of contacts returned
    :param offset: int: Specify the offset of the query
    :param ge: Specify that the value must be greater than or equal to 10
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, tags=['contacts'],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    It requires an authorization token in order to access it.

    :param contact_id: int: Specify the contact id in the url path
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user from the auth_service
    :return: A contact object, which is a pydantic model
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


@router.get('/birthday/{birthday_days}', response_model=list[ContactResponse], tags=['contacts'],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_birthday_contacts(birthday_days: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_birthday_contacts function returns a list of contacts that have birthdays within the next
        number of days specified by the birthday_days parameter. The user is authenticated using the auth_service,
        and then passed to repository_contacts.get_birthday_contacts along with db and birthday days.

    :param birthday_days: int: Specify the number of days to look ahead for birthdays
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :return: A list of contacts with a birthday in the next x days
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_birthday_contacts(birthday_days, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found...')
    return contacts


@router.post('/', response_model=ContactResponse, tags=['contacts'], status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user from the auth_service
    :return: A contactschema object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}', response_model=ContactResponse, tags=['contacts'])
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id of the contact to be updated, and a body containing all fields that need to be updated.
        If no body is provided, then nothing will be changed in the database.

    :param body: ContactSchema: Validate the request body and convert it into a contact object
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact id to be deleted
    :param db: Session: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list containing the id, name and email of the deleted contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact.scalars().all()


@router.get('/by_params/', response_model=list[ContactResponse], tags=['contacts'])
async def get_contacts_by_params(name: str | None = None, surname: str | None = None, email: str | None = None,
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_params function is used to retrieve contacts from the database.
        The function takes in a name, surname and email as parameters.
        If no parameters are provided, all contacts will be returned.

    :param name: str | None: Filter the contacts by name
    :param surname: str | None: Filter the contacts by surname
    :param email: str | None: Search for a contact by email
    :param db: AsyncSession: Get the database session
    :param user: User: Get the user from the database
    :return: A list of contacts that match the parameters
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts_by_params(name, surname, email, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found...')
    return contacts
