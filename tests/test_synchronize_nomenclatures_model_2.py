import os
import unittest
from datetime import datetime
from uuid import uuid4, UUID

from sqlmodel import Session, create_engine, select
from chromadb import HttpClient

from infra.chroma_store import connect_to_chroma_collection, drop_collection, create_collection
from model.synchronize_nomenclatures_model import synchronize_nomenclatures
import pytest

from scheme.nomenclature_scheme import MsuDatabaseOneNomenclatureRead

all_noms_guids = [uuid4() for _ in range(10)]

noms_to_create = [all_noms_guids[1], all_noms_guids[3], all_noms_guids[6]]

root_link = UUID("e29a2c8c-dad2-11ea-8e35-001e67bc1b0d")
root_parent = UUID("00000000-0000-0000-0000-000000000000")

@pytest.fixture
def _db_params():
    print("_chroma_params starts")
    demo_stand_db_con_str = "mssql+pyodbc://test:!1Testtest@mssql-129364-0.cloudclusters.net:15827/test_dwh?driver=ODBC+Driver+17+for+SQL+Server"
    demo_stand_table_name = "СправочникНоменклатура"
    demo_stand_schema = "us"
    return demo_stand_db_con_str, demo_stand_table_name, demo_stand_schema

@pytest.fixture
def _chroma_params():
    print("_chroma_params starts")
    os.environ['CHROMA_HOST'] = "45.8.98.160"
    os.environ['CHROMA_PORT'] = "8000"
    demo_stand_chroma_collection_name = "test_nomenclature"
    print("_chroma_params finished")
    return demo_stand_chroma_collection_name


@pytest.fixture
def _drop_test_nomenclature_db_table(_db_params):
    print("Drop db table starts")
    demo_stand_db_con_str, table_name, schema = _db_params
    engine = create_engine(demo_stand_db_con_str)
    with engine.connect() as con:
        if engine.dialect.has_table(
            con,
            MsuDatabaseOneNomenclatureRead.__tablename__,
            schema=MsuDatabaseOneNomenclatureRead.__table_args__["schema"]
        ):
            MsuDatabaseOneNomenclatureRead.__table__.drop(bind=engine)
    print("Drop db table finished")


@pytest.fixture
def _recreate_test_nomenclature_db_table(_drop_test_nomenclature_db_table, _db_params):
    print("Drop recreate test starts")
    demo_stand_db_con_str, table_name, schema = _db_params
    engine = create_engine(demo_stand_db_con_str)
    MsuDatabaseOneNomenclatureRead.__table__.create(bind=engine)
    print("Drop recreate test finished")


@pytest.fixture
def _drop_test_nomenclature_chroma_collection(_chroma_params):
    print("Drop chroma collection starts")
    demo_stand_chroma_collection_name = _chroma_params
    drop_collection(demo_stand_chroma_collection_name)
    print("Drop chroma collection finished")


@pytest.fixture
def _recreate_test_nomenclature_chroma_collection(_drop_test_nomenclature_chroma_collection, _chroma_params):
    print("Create chroma collection starts")
    demo_stand_chroma_collection_name = _chroma_params
    create_collection(demo_stand_chroma_collection_name)
    print("Create chroma collection finished")


@pytest.fixture
def _create_test_noms(_recreate_test_nomenclature_db_table, _db_params):
    print("Create noms starts")
    demo_stand_db_con_str, table_name, schema = _db_params
    engine = create_engine(demo_stand_db_con_str)
    test_nomenclatures_and_groups = [
        MsuDatabaseOneNomenclatureRead(
            id=root_link,
            is_deleted=False,
            nomenclature_name="0001 Новая структура справочника",
            group=root_parent,
            is_group=True,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[1],
            is_deleted=False,
            nomenclature_name="Объект 1-1",
            group=root_link,
            is_group=False,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[2],
            is_deleted=False,
            nomenclature_name="Группа 1-2",
            group=root_link,
            is_group=True,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[3],
            is_deleted=False,
            nomenclature_name="Объект 1-2-1",
            group=all_noms_guids[2],
            is_group=False,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[4],
            is_deleted=True,
            nomenclature_name="Объект 1-2-2",
            group=all_noms_guids[2],
            is_group=False,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[5],
            is_deleted=False,
            nomenclature_name="Группа 1-3",
            group=root_link,
            is_group=True,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[6],
            is_deleted=False,
            nomenclature_name="Объект 1-3-1",
            group=all_noms_guids[5],
            is_group=False,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[7],
            is_deleted=True,
            nomenclature_name="Объект 1-3-2",
            group=all_noms_guids[5],
            is_group=False,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[8],
            is_deleted=False,
            nomenclature_name="0002 Старая структура",
            group=root_parent,
            is_group=True,
            edited_at=datetime.now()
        ),
        MsuDatabaseOneNomenclatureRead(
            id=all_noms_guids[9],
            is_deleted=False,
            nomenclature_name="Объект 2-1",
            group=all_noms_guids[8],
            is_group=False,
            edited_at=datetime.now()
        )
    ]

    with Session(engine) as session:
        session.add_all(test_nomenclatures_and_groups)
        session.commit()

    print("Create noms finished")


@pytest.fixture
def _update_test_noms(_db_params):
    demo_stand_db_con_str, table_name, schema = _db_params
    engine = create_engine(demo_stand_db_con_str)

    with Session(engine) as session:
        nom_1 = session.scalars(select(MsuDatabaseOneNomenclatureRead).where(MsuDatabaseOneNomenclatureRead.id == str(all_noms_guids[1]))).one()
        nom_1.nomenclature_name = "Объект 1-1 поменялось"
        nom_2 = session.scalars(select(MsuDatabaseOneNomenclatureRead).where(MsuDatabaseOneNomenclatureRead.id == str(all_noms_guids[3]))).one()
        nom_2.nomenclature_name = "Объект 1-2-1 поменялось"
        nom_3 = session.scalars(select(MsuDatabaseOneNomenclatureRead).where(MsuDatabaseOneNomenclatureRead.id == str(all_noms_guids[6]))).one()
        nom_3.is_deleted = True
        session.add_all([nom_1, nom_2, nom_3])
        session.commit()


class TestIntegrationSyncNomsModel:
    def _get_chroma_result(self, demo_stand_chroma_collection_name: str):
        chroma_client = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
        collection = chroma_client.get_collection(demo_stand_chroma_collection_name)
        chroma_result = collection.get()
        ids = chroma_result["ids"]
        return ids

    @pytest.mark.dependency()
    def test_creating_noms_in_chroma(
        self,
        _recreate_test_nomenclature_chroma_collection,
        _create_test_noms,
        _db_params,
        _chroma_params
    ):
        answers_noms_to_create_in_chroma = [all_noms_guids[1], all_noms_guids[3], all_noms_guids[6]]
        answers_noms_to_create_in_chroma = [str(a) for a in answers_noms_to_create_in_chroma]
        sync_period = 24
        demo_stand_db_con_str, _, _ = _db_params
        demo_stand_chroma_collection_name = _chroma_params

        synchronize_nomenclatures(
            nom_db_con_str=demo_stand_db_con_str,
            chroma_collection_name=demo_stand_chroma_collection_name,
            sync_period=sync_period
        )

        collection = connect_to_chroma_collection(demo_stand_chroma_collection_name)
        chroma_result = collection.get(include=["embeddings"])

        print(chroma_result)

        unittest.TestCase().assertCountEqual(chroma_result["ids"], answers_noms_to_create_in_chroma)
        assert len(chroma_result["embeddings"]) == 3

    @pytest.mark.dependency(depends=["test_creating_noms_in_chroma"])
    def test_updating_and_deleting_noms_in_chroma(
        self,
        _update_test_noms,
        _db_params,
        _chroma_params
    ):
        sync_period = 24
        demo_stand_db_con_str, _, _ = _db_params
        demo_stand_chroma_collection_name = _chroma_params

        collection = connect_to_chroma_collection(demo_stand_chroma_collection_name)

        nom_1_before = collection.get(ids=str(all_noms_guids[1]), include=["embeddings"])
        nom_2_before = collection.get(ids=str(all_noms_guids[3]), include=["embeddings"])

        synchronize_nomenclatures(
            nom_db_con_str=demo_stand_db_con_str,
            chroma_collection_name=demo_stand_chroma_collection_name,
            sync_period=sync_period
        )

        nom_1_after = collection.get(ids=str(all_noms_guids[1]), include=["embeddings"])
        nom_2_after = collection.get(ids=str(all_noms_guids[3]), include=["embeddings"])
        nom_3 = collection.get(ids=str(all_noms_guids[6]), include=["embeddings"])

        assert nom_1_before["embeddings"] != nom_1_after["embeddings"]
        assert nom_2_before["embeddings"] != nom_2_after["embeddings"]
        assert nom_3["ids"] == []
