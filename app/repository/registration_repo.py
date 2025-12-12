from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.models import Registration
from app.schemas import RegistrationIn


def get_registration_by_uid(db: Session, user_id: int, eager_load: bool = False) -> Registration | None:
    query = db.query(Registration).filter(Registration.uid == user_id)
    if eager_load:
        # 预加载 attachments 关系
        query = query.options(joinedload(Registration.attachments))
    return query.first()


def create_registration(db: Session, data: RegistrationIn, user_id: int) -> Registration:
    reg = Registration(
        uid=user_id,
        note=data.note,
        status="pending"
    )
    db.add(reg)
    return reg


def get_registration_by_id(db: Session, registration_id: int, eager_load: bool = True) -> Registration | None:
    query = db.query(Registration)
    if eager_load:
        query = query.options(joinedload(Registration.attachments))
    return query.filter(Registration.registrationId == registration_id).first()


def list_registrations(db: Session, status: str | None, page: int, page_size: int):
    q = db.query(Registration)
    if status:
        q = q.filter(Registration.status == status)
    total = q.count()
    items = (
        q.options(joinedload(Registration.attachments))
        .order_by(Registration.createdAt.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_registration_status(db: Session, reg: Registration, status: str) -> Registration:
    reg.status = status
    db.add(reg)
    return reg


def delete_registration(db: Session, reg: Registration):
    db.delete(reg)
