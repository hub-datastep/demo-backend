from sqlmodel import Session

from scheme.mode.mode_scheme import Mode, ModeCreate


def get_mode_by_id(session: Session, mode_id: int) -> Mode | None:
    mode = session.get(Mode, mode_id)
    return mode


def create_mode(session: Session, mode: ModeCreate) -> Mode:
    mode_db = Mode.from_orm(mode)
    session.add(mode_db)
    session.commit()
    return mode_db
