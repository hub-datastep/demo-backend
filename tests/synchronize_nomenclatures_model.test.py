import os
from datetime import datetime

from sqlalchemy import create_engine, text

from infra.chroma_store import connect_to_chroma_collection, delete_embeddings, is_in_vectorstore
from model.synchronize_nomenclatures_model import synchronize_nomenclatures

demo_stand_db_con_str = "postgresql://postgres:jdDBwfIWizA6IdlW@45.8.98.160:5432/postgres"
engine = create_engine(demo_stand_db_con_str)

all_noms_guids = [
    "e29a2c8c-dad2-11ea-8e35-001e67bc1b0d",
    "2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02",
    "eab8f49a-67b8-4f44-aafe-30dfcf9f0f59",
    "fbf2874e-7d94-4621-95fd-6d5c5d1289d8",
    "ffa4a1c6-78fc-40c0-94c4-462ab95332bb",
    "c791a3b0-06e1-4f70-8db4-33b12f43ac43",
    "bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7",
    "5f07377b-cd67-4e8d-a834-ff485a9c3a9f",
    "7d3c8e2a-2295-4785-90a5-204007cc24fb",
    "2e1c2b51-c0d4-4de4-b3ab-460bc891e1d8"
]

noms_to_create_or_update = [
    "2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02",
    "fbf2874e-7d94-4621-95fd-6d5c5d1289d8",
    "bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7",
]

root_link = "e29a2c8c-dad2-11ea-8e35-001e67bc1b0d"
root_parent = "00000000-0000-0000-0000-000000000000"


def _drop_test_nomenclature_table(table_name: str, schema: str):
    st = text(f"""
        DROP SCHEMA IF EXISTS {schema} CASCADE;
        DROP TABLE IF EXISTS {schema}.{table_name} CASCADE;
    """)

    with engine.connect() as connection:
        connection.execute(st)
        connection.commit()


def _create_test_nomenclature_table(table_name: str, schema: str):
    st = text(f"""
        CREATE SCHEMA IF NOT EXISTS {schema};
        
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            "Ссылка" UUID PRIMARY KEY,
            "ПометкаУдаления" INT,
            "Наименование" TEXT,
            "Родитель" UUID,
            "ЭтоГруппа" INT,
            "МСУ_ДатаИзменения" TIMESTAMP
        );
    """)

    with engine.connect() as connection:
        connection.execute(st)
        connection.commit()


def _create_test_noms(table_name: str, schema: str):
    st = text(f"""
    INSERT INTO {schema}.{table_name}(
        Ссылка, 
        ПометкаУдаления,
        Наименование,
        Родитель,
        ЭтоГруппа,
        МСУ_ДатаИзменения
   )
    VALUES
    (
        '{root_link}',
        0,
        '0001 Новая структура справочника',
        '{root_parent}',
        1,
        '{datetime.now()}'
    ),
        (
            '2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02',
            0,
            'Объект 1-1', 
            '{root_link}',
            0, 
            '{datetime.now()}'
        ),
        (
            'eab8f49a-67b8-4f44-aafe-30dfcf9f0f59',
            0,
            'Группа 1-2', 
            '{root_link}', 
            1, 
            '{datetime.now()}'
        ),
            (
                'fbf2874e-7d94-4621-95fd-6d5c5d1289d8',
                0,
                'Объект 1-2-1',
                'eab8f49a-67b8-4f44-aafe-30dfcf9f0f59',
                0,
                '{datetime.now()}'
            ),
            (
                'ffa4a1c6-78fc-40c0-94c4-462ab95332bb',
                1,
                'Объект 1-2-2', 
                'eab8f49a-67b8-4f44-aafe-30dfcf9f0f59', 
                0, 
                '{datetime.now()}'
            ),
        (
            'c791a3b0-06e1-4f70-8db4-33b12f43ac43',
            0,
            'Группа 1-3', 
            '{root_link}', 
            1, 
            '{datetime.now()}'
        ),
            (
                'bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7',  
                0,
                'Объект 1-3-1', 
                'c791a3b0-06e1-4f70-8db4-33b12f43ac43', 
                0,
                '{datetime.now()}'
            ),
            (
                '5f07377b-cd67-4e8d-a834-ff485a9c3a9f', 
                1,
                'Объект 1-3-2', 
                'c791a3b0-06e1-4f70-8db4-33b12f43ac43', 
                0,
                '{datetime.now()}'
            ),
    
    
    (
        '7d3c8e2a-2295-4785-90a5-204007cc24fb', 
        0,
        '0002 Старая структура', 
        '{root_parent}',
        1,
        '{datetime.now()}'
    ),
        (
            '2e1c2b51-c0d4-4de4-b3ab-460bc891e1d8', 
            0,
            'Объект 2-1', 
            '7d3c8e2a-2295-4785-90a5-204007cc24fb', 
            0,
            '{datetime.now()}'
        );
    """)

    with engine.connect() as connection:
        connection.execute(st)
        connection.commit()


def _update_test_noms(table_name: str, schema: str):
    st = text(f"""
    UPDATE {schema}.{table_name}
    SET "Наименование" = 'Объект 1-1 поменялось'
    WHERE "Ссылка" = '2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02';
    
    UPDATE {schema}.{table_name}
    SET "Наименование" = 'Объект 1-2-1 поменялось'
    WHERE "Ссылка" = 'fbf2874e-7d94-4621-95fd-6d5c5d1289d8';
    
    UPDATE {schema}.{table_name}
    SET "ПометкаУдаления" = 1
    WHERE "Ссылка" = 'bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7';
    """)

    with engine.connect() as connection:
        connection.execute(st)
        connection.commit()


if __name__ == "__main__":
    """
    Должно добавиться 3 номенклатуры с "Ссылка":
    - 2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02 (Объект 1-1)
    - fbf2874e-7d94-4621-95fd-6d5c5d1289d8 (Объект 1-2-1)
    - bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7 (Объект 1-3-1)
    
    Потом должно поменяться 2 номенклатуры с "Ссылка":
    - 2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02 (Объект 1-1)
    - fbf2874e-7d94-4621-95fd-6d5c5d1289d8 (Объект 1-2-1)
    
    И удалиться 1 номенклатур с "Ссылка":
    - bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7 (Объект 1-3-1)
    """

    demo_stand_table_name = "СправочникНоменклатура"
    demo_stand_schema = "us"
    demo_stand_chroma_collection_name = "nomenclature"

    print(f"Dropping test table: {demo_stand_schema}.{demo_stand_table_name} ...")
    _drop_test_nomenclature_table(demo_stand_table_name, demo_stand_schema)
    print(f"Table dropped.")

    print(f"Creating test table: {demo_stand_schema}.{demo_stand_table_name} ...")
    _create_test_nomenclature_table(demo_stand_table_name, demo_stand_schema)
    print(f"Table created.")

    print(f"Creating test noms...")
    _create_test_noms(demo_stand_table_name, demo_stand_schema)
    print(f"Noms created.")

    os.environ['CHROMA_HOST'] = "45.8.98.160"
    os.environ['CHROMA_PORT'] = "8000"

    collection = connect_to_chroma_collection(demo_stand_chroma_collection_name)

    # Clear chroma from test noms & groups
    print(f"Clear test embeddings before tests...")
    delete_embeddings(
        collection=collection,
        ids=all_noms_guids
    )
    print(f"Test embeddings cleared.")

    # Must create all in noms_to_create_or_update
    print(f"First test sync of noms...")
    synchronize_nomenclatures(
        nom_db_con_str=demo_stand_db_con_str,
        chroma_collection_name=demo_stand_chroma_collection_name,
        sync_period=24,
    )
    # is_new_noms_created must be all True
    is_new_noms_created = [is_in_vectorstore(collection=collection, ids=guid) for guid in noms_to_create_or_update]
    assert is_new_noms_created.count(True) == len(noms_to_create_or_update)
    print(f"First test is OK.")

    print(f"Updating some noms...")
    _update_test_noms(demo_stand_table_name, demo_stand_schema)
    print(f"Noms updated...")

    # Must update first 2 in noms_to_create_or_update
    # and delete last 1 in noms_to_create_or_update
    print(f"Second test sync of noms...")
    synchronize_nomenclatures(
        nom_db_con_str=demo_stand_db_con_str,
        chroma_collection_name=demo_stand_chroma_collection_name,
        sync_period=24,
    )
    # is_new_noms_updated_or_deleted must be first 2 True
    is_new_noms_updated_or_deleted = [
        is_in_vectorstore(collection=collection, ids=guid) for guid in noms_to_create_or_update
    ]
    assert is_new_noms_updated_or_deleted.count(True) == len(noms_to_create_or_update) - 1
    print(f"Second test is OK.")

    # Clear chroma after tests
    print(f"Clear test embeddings before tests...")
    delete_embeddings(
        collection=collection,
        ids=all_noms_guids
    )
    print(f"Test embeddings cleared.")

    print(f"Dropping test table after tests: {demo_stand_schema}.{demo_stand_table_name} ...")
    _drop_test_nomenclature_table(demo_stand_table_name, demo_stand_schema)
    print(f"Table dropped.")

    pass
