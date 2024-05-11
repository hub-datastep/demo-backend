from sqlmodel import Session, select

from scheme.file_scheme import File, FileCreate


def get_all_filenames_by_tenant_id(session: Session, tenant_id: int) -> list[File]:
    statement = select(File).where(File.tenant_id == tenant_id)
    result = session.exec(statement)
    return list(result.all())


def save_file(session: Session, new_file: FileCreate) -> File:
    file = File.from_orm(new_file)
    session.add(file)
    session.commit()
    session.refresh(file)
    return file


def get_file_by_id(session: Session, file_id: int) -> File | None:
    file = session.get(File, file_id)
    return file


def delete_file(session: Session, file: File) -> None:
    session.delete(file)
    session.commit()
