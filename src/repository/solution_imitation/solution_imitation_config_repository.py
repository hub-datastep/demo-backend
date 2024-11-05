from sqlmodel import Session, select
from scheme.solution_imitation.solution_imitation_config_scheme import (
    SolutionImitationConfig,
)


def get_config_by_type_and_user_id(
    session: Session,
    type: str,
    user_id: int,
) -> SolutionImitationConfig | None:
    st = select(SolutionImitationConfig)
    st = st.where(SolutionImitationConfig.user_id == user_id)
    st = st.where(SolutionImitationConfig.type == type)

    config = session.exec(st).first()

    return config
