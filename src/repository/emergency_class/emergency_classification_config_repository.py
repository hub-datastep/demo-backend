from sqlmodel import Session, select

from infra.database import engine
from scheme.emergency_class.emergency_classification_config_scheme import EmergencyClassificationConfig

# ID of empty user
DEFAULT_CONFIG_USER_ID = 0


def get_default_config() -> EmergencyClassificationConfig | None:
    with Session(engine) as session:
        config = session.get(EmergencyClassificationConfig, DEFAULT_CONFIG_USER_ID)
        return config


def get_config_by_user_id(session: Session, user_id: int) -> EmergencyClassificationConfig | None:
    st = select(EmergencyClassificationConfig)
    st = st.where(EmergencyClassificationConfig.user_id == user_id)
    config = session.exec(st).first()
    return config
