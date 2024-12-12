from sqlmodel import Session, select

from infra.database import engine
from scheme.order_classification.order_classification_config_scheme import (
    OrderClassificationConfig,
)

# ID of empty user
DEFAULT_CONFIG_USER_ID = 0
# For tests
# DEFAULT_CONFIG_USER_ID = 8


def get_default_config(
    client: str | None = None,
) -> OrderClassificationConfig | None:
    with Session(engine) as session:
        st = select(OrderClassificationConfig)
        st = st.where(OrderClassificationConfig.user_id == DEFAULT_CONFIG_USER_ID)
        st = st.where(OrderClassificationConfig.client == client)

        config = session.exec(st).first()

        return config


def get_config_by_user_id(
    session: Session,
    user_id: int,
) -> OrderClassificationConfig | None:
    st = select(OrderClassificationConfig)
    st = st.where(OrderClassificationConfig.user_id == user_id)
    config = session.exec(st).first()
    return config
