from sqlalchemy.orm import Session
from datetime import date, timedelta

from contacts_api.models import Contact, User
from .models import User, Contact
from .schemas import UserCreate, ContactCreate, ContactUpdate
from .auth import auth_service


class UserCRUD:
    @staticmethod
    async def get_user_by_email(email: str, db: Session) -> type[User] | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    async def get_user_by_id(user_id: int, db: Session) -> type[User] | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> User | None:
        existing_user = await UserCRUD.get_user_by_email(user.email, db)
        if existing_user:
            return None

        hashed_password = auth_service.get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


class ContactCRUD:
    @staticmethod
    def create(contact: ContactCreate, owner_id: int, db: Session) -> Contact:
        db_contact = Contact(**contact.model_dump(), owner_id=owner_id)
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact

    @staticmethod
    def get_by_id(contact_id: int, owner_id: int, db: Session) -> type[Contact] | None:
        return db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.owner_id == owner_id
        ).first()

    @staticmethod
    def get_all(owner_id: int, db: Session) -> list[type[Contact]]:
        return db.query(Contact).filter(Contact.owner_id == owner_id).all()

    @staticmethod
    def search(owner_id: int, db: Session, first_name: str = None, last_name: str = None, email: str = None):
        query = db.query(Contact).filter(Contact.owner_id == owner_id)
        if first_name:
            query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(Contact.email.ilike(f"%{email}%"))
        return query.all()

    @staticmethod
    def update(contact_id: int, owner_id: int, contact_update: ContactUpdate, db: Session):
        db_contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.owner_id == owner_id
        ).first()
        if db_contact:
            for field, value in contact_update.model_dump(exclude_unset=True).items():
                setattr(db_contact, field, value)
            db.commit()
            db.refresh(db_contact)
        return db_contact

    @staticmethod
    def delete(contact_id: int, owner_id: int, db: Session) -> bool:
        db_contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.owner_id == owner_id
        ).first()
        if db_contact:
            db.delete(db_contact)
            db.commit()
            return True
        return False

    @staticmethod
    def get_birthdays(owner_id: int, db: Session, days: int = 7):
        today = date.today()
        end_date = today + timedelta(days=days)
        contacts = db.query(Contact).filter(Contact.owner_id == owner_id).all()
        birthday_contacts = []
        for contact in contacts:
            birthday_this_year = contact.birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = contact.birthday.replace(year=today.year + 1)
            if today <= birthday_this_year <= end_date:
                birthday_contacts.append(contact)
        return birthday_contacts