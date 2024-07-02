from sqlmodel import Session

from scheme.mode.mode_scheme import Mode, ModeCreate


def create_mode(session: Session, mode: ModeCreate) -> Mode:
    mode_db = Mode.from_orm(mode)
    session.add(mode_db)
    session.commit()
    return mode_db
