import json
import os

import pytest
from fastapi.testclient import TestClient
from sshtunnel import SSHTunnelForwarder

from app import app
from model import nomenclature_model
from scheme.nomenclature_scheme import MappingOneNomenclatureUpload


def set_vpn_tunnel_and_get_local_port(
    ssh_host: str,
    ssh_port: int,
    ssh_username: str,
    ssh_password: str,
    remote_bind_host: str,
    remote_bind_port: int
):
    jump_host_tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=(remote_bind_host, remote_bind_port)
    )
    jump_host_tunnel.start()
    return jump_host_tunnel.local_bind_port


@pytest.fixture
def _set_chroma_vpn_port():
    jump_host_port = set_vpn_tunnel_and_get_local_port(
        os.getenv("JUMP_HOST_HOST"), int(os.getenv("JUMP_HOST_PORT")),
        os.getenv("JUMP_HOST_USERNAME"), os.getenv("JUMP_HOST_PASSWORD"),
        os.getenv("DEV_HOST_HOST"), int(os.getenv("DEV_HOST_PORT"))
    )
    chroma_port = set_vpn_tunnel_and_get_local_port(
        "localhost", jump_host_port,
        os.getenv("DEV_HOST_USERNAME"), os.getenv("DEV_HOST_PASSWORD"),
        "localhost", int(os.getenv("DEV_HOST_CHROMA_PORT"))
    )
    os.environ["CHROMA_PORT"] = str(chroma_port)


@pytest.fixture
def _test_client():
    return TestClient(app)


def test_mapping_model(_set_chroma_vpn_port, _test_client):
    """
    Для этого теста важно использовать классификатор 141223.

    Для кейса «Труба полипропиленовая армированная стекловолокном SDR6 PN25 25 х 4.2 мм хлыст 4м белая»
    классификатор выдаёт группу, которой нет в векторсторе.

    Для кейса «Выключатель накладной Reone 1клавиша,цвет белый»
    классификатор выдаёт группу, которой есть в векторсторе.
    """
    test_nomenclatures = [
        MappingOneNomenclatureUpload(
            row_number=1,
            nomenclature="Труба полипропиленовая армированная стекловолокном SDR6 PN25 25 х 4.2 мм хлыст 4м белая"
        ),
        MappingOneNomenclatureUpload(
            row_number=1,
            nomenclature="Выключатель накладной Reone 1клавиша,цвет белый"
        )
    ]
    most_similar_count = 3

    result_as_json = nomenclature_model.process(
        nomenclatures=test_nomenclatures,
        most_similar_count=most_similar_count,
        chroma_collection_name="nomenclature",
        model_id="141223",
        use_jobs=False
    )
    result_as_dict = json.loads(result_as_json)

    assert result_as_dict[0]["mappings"] is None
    assert result_as_dict[1]["mappings"] is not None
    assert len(result_as_dict[1]["mappings"]) == most_similar_count
