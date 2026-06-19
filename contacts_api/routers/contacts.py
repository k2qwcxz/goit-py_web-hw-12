from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from contacts_api.database import get_db
from contacts_api.schemas import ContactCreate, ContactUpdate, ContactResponse
from contacts_api.crud import ContactCRUD
from contacts_api.models import User
from contacts_api.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return ContactCRUD.create(contact, current_user.id, db)


@router.get("/", response_model=list[ContactResponse])
async def get_all_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return ContactCRUD.get_all(current_user.id, db)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = ContactCRUD.get_by_id(contact_id, current_user.id, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(
    first_name: str = Query(None),
    last_name: str = Query(None),
    email: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    if not any([first_name, last_name, email]):
        raise HTTPException(status_code=400, detail="Provide at least one search parameter")
    return ContactCRUD.search(current_user.id, db, first_name, last_name, email)


@router.get("/birthdays/upcoming", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return ContactCRUD.get_birthdays(current_user.id, db, days)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = ContactCRUD.update(contact_id, current_user.id, contact_update, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    success = ContactCRUD.delete(contact_id, current_user.id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")