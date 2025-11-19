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