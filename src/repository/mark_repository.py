from sqlmodel import Session, select

from scheme.mark_scheme import MarkCreate, Mark


def create_or_update_mark(session: Session, mark: MarkCreate) -> Mark:
    statement = select(Mark).where(Mark.message_id == mark.message_id)
    result = session.exec(statement)
    mark_db = result.first()

    if mark_db is None:
        mark_db = Mark.from_orm(mark)
        session.add(mark_db)
        session.commit()
        return mark_db

    mark_db.mark = mark.mark
    session.add(mark_db)
    session.commit()

    return mark_db


# class MarkRepository:
#     @classmethod
#     def fetch_by_message_id(cls, message_id: int) -> MarkOutDto:
#         message = message_repository.fetch_by_id(message_id)
#         return message.mark
#
#     @classmethod
#     def create(cls, body: MarkCreateDto) -> MarkOutDto:
#         (_, marks), _ = supabase.table("mark").select("*").eq("message_id", body.message_id).execute()
#
#         if len(marks) == 0:
#             (_, [mark]), _ = supabase.table("mark").insert(body.model_dump()).execute()
#             return mark
#
#         (_, [mark]), _ = supabase.table("mark").update(body.model_dump()).eq("message_id", body.message_id).execute()
#         return MarkOutDto(**mark)
#
#
# mark_repository = MarkRepository()
