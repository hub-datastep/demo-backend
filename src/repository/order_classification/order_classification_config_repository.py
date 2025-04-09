from sqlmodel import Session, select

from infra.database import engine
from repository.base import BaseRepository
from scheme.order_classification.order_classification_config_scheme import (
    OrderClassificationConfig,
)

# ID of empty user
DEFAULT_CONFIG_ID = 0
# For tests
# DEFAULT_CONFIG_ID = 8


def get_default_config(
    client: str | None = None,
) -> OrderClassificationConfig | None:
    with Session(engine) as session:
        st = select(OrderClassificationConfig)
        st = st.where(OrderClassificationConfig.id == DEFAULT_CONFIG_ID)
        st = st.where(OrderClassificationConfig.client == client)

        config = session.exec(st).first()

        return config


def get_config_by_id(
    config_id: int,
) -> OrderClassificationConfig | None:
    with Session(engine) as session:
        config = session.get(OrderClassificationConfig, config_id)
        return config


def get_config_by_user_id(
    session: Session,
    user_id: int,
) -> OrderClassificationConfig | None:
    st = select(OrderClassificationConfig)
    st = st.where(OrderClassificationConfig.user_id == user_id)
    config = session.exec(st).first()
    return config


class OrderClassificationConfigRepository(BaseRepository[OrderClassificationConfig]):
    """
    Repository for OrderClassificationConfig DB table.
    """

    def __init__(self) -> None:
        super().__init__(schema=OrderClassificationConfig)


order_classification_config_repository = OrderClassificationConfigRepository()
