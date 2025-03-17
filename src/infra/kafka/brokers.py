from scheme.kafka.broker_settings_scheme import KafkaBrokerSettings

from infra.env import env
from infra.kafka.helpers import create_kafka_broker


# * Unistroy Kafka Broker
_unistroy_servers_list = env.UNISTROY_KAFKA_SERVERS.split(",")
_unistroy_broker_settings = KafkaBrokerSettings(
    servers_list=_unistroy_servers_list,
    username=env.UNISTROY_KAFKA_USERNAME,
    password=env.UNISTROY_KAFKA_PASSWORD,
    is_use_ssl=env.UNISTROY_IS_KAFKA_WITH_SSL,
    ssl_cert_file_path=env.UNISTROY_SSL_CERT_FILE_PATH,
)
unistroy_kafka_broker = create_kafka_broker(
    settings=_unistroy_broker_settings,
)

# * Internal Kafka Broker
_servers_list = env.KAFKA_SERVERS.split(",")
_broker_settings = KafkaBrokerSettings(
    servers_list=_servers_list,
    username=env.KAFKA_USERNAME,
    password=env.KAFKA_PASSWORD,
)
kafka_broker = create_kafka_broker(
    settings=_broker_settings,
)
