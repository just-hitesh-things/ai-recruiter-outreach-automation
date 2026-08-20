from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import DEFAULT_CONTACT_STATUS, Contact
from ..schemas import ContactCreate, ContactRead

PENDING_BATCH_SIZE = 5
SENT_STATUS = "sent"

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.post(
    "/",
    response_model=ContactRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db),
) -> Contact:
    contact = Contact(
        name=payload.name.strip(),
        email=str(payload.email).lower(),
        title=payload.title.strip(),
        company=payload.company.strip(),
    )
    db.add(contact)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A contact with this email already exists.",
        ) from None
    await db.refresh(contact)
    return contact


@router.get("/pending", response_model=list[ContactRead])
async def get_pending_contacts(db: AsyncSession = Depends(get_db)) -> list[Contact]:
    """Return up to 5 contacts that n8n has not emailed yet (status = new)."""
    result = await db.execute(
        select(Contact)
        .where(Contact.status == DEFAULT_CONTACT_STATUS)
        .order_by(Contact.date_added.asc())
        .limit(PENDING_BATCH_SIZE)
    )
    return list(result.scalars().all())


@router.put("/{contact_id}/status", response_model=ContactRead)
async def mark_contact_sent(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Contact:
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    contact.status = SENT_STATUS
    contact.date_emailed = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(contact)
    return contact
