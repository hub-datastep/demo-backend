import os

from sqlalchemy import create_engine, text

demo_stand_db_con_str = "postgresql://postgres:jdDBwfIWizA6IdlW@45.8.98.160:5432/postgres"
engine = create_engine(demo_stand_db_con_str)


def create_nomenclature_table(table_name: str):
    st = text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            "Ссылка" UUID PRIMARY KEY,
            "ПометкаУдаления" INT,
            "Наименование" VARCHAR(255),
            "Родитель" UUID,
            "ЭтоГруппа" INT,
            "МСУ_ДатаИзменения" DATE
        );
    """)

    with engine.connect() as connection:
        connection.execute(st)
        connection.commit()
    # return read_sql(st, db_con_str)


def create_test_noms(table_name: str):
    root_link = "e29a2c8c-dad2-11ea-8e35-001e67bc1b0d"
    root_parent = "00000000-0000-0000-0000-000000000000"

    st = text(f"""
    INSERT INTO {table_name}(
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
        '2024-03-21'
    ),
        (
            '2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02',
            0,
            'Объект 1-1', 
            '{root_link}',
            0, 
            '2024-03-21'
        ),
        (
            'eab8f49a-67b8-4f44-aafe-30dfcf9f0f59',
            0,
            'Группа 1-2', 
            '{root_link}', 
            1, 
            '2024-03-21'
        ),
            (
                'fbf2874e-7d94-4621-95fd-6d5c5d1289d8',
                0,
                'Объект 1-2-1',
                'eab8f49a-67b8-4f44-aafe-30dfcf9f0f59',
                0,
                '2024-03-21'
            ),
            (
                'ffa4a1c6-78fc-40c0-94c4-462ab95332bb',
                1,
                'Объект 1-2-2', 
                'eab8f49a-67b8-4f44-aafe-30dfcf9f0f59', 
                0, 
                '2024-03-21'
            ),
        (
            'c791a3b0-06e1-4f70-8db4-33b12f43ac43',
            0,
            'Группа 1-3', 
            '{root_link}', 
            1, 
            '2024-03-21'
        ),
            (
                'bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7',  
                0,
                'Объект 1-3-1', 
                'c791a3b0-06e1-4f70-8db4-33b12f43ac43', 
                0,
                '2024-03-21'
            ),
            (
                '5f07377b-cd67-4e8d-a834-ff485a9c3a9f', 
                1,
                'Объект 1-3-2', 
                'c791a3b0-06e1-4f70-8db4-33b12f43ac43', 
                0,
                '2024-03-21'
            ),
    
    
    (
        '7d3c8e2a-2295-4785-90a5-204007cc24fb', 
        0,
        '0002 Старая структура', 
        '{root_parent}',
        1,
        '2024-03-21'
    ),
        (
            '2e1c2b51-c0d4-4de4-b3ab-460bc891e1d8', 
            0,
            'Объект 2-1', 
            '7d3c8e2a-2295-4785-90a5-204007cc24fb', 
            0,
            '2024-03-21'
        );
    """)

    with engine.connect() as connection:
        connection.execute(st)
        connection.commit()


if __name__ == "__main__":
    demo_stand_table_name = "СправочникНоменклатураТест"
    demo_stand_chroma_collection_name = "nomenclature"

    # print(f"Creating test table: {demo_stand_table_name} ...")
    # create_nomenclature_table(demo_stand_table_name)
    # print(f"Table created.")

    # print(f"Creating test noms...")
    # create_test_noms(demo_stand_table_name)
    # print(f"Noms created.")

    os.environ['CHROMA_HOST'] = "45.8.98.160"
    os.environ['CHROMA_PORT'] = "8000"

    # Clear chroma from test noms & groups
    # collection = connect_to_chroma_collection(demo_stand_chroma_collection_name)
    # delete_embeddings(
    #     collection=collection,
    #     ids=[
    #         "e29a2c8c-dad2-11ea-8e35-001e67bc1b0d",
    #         "2c7a39bf-f4e6-4c16-a6e6-bd82a4478d02",
    #         "eab8f49a-67b8-4f44-aafe-30dfcf9f0f59",
    #         "fbf2874e-7d94-4621-95fd-6d5c5d1289d8",
    #         "ffa4a1c6-78fc-40c0-94c4-462ab95332bb",
    #         "c791a3b0-06e1-4f70-8db4-33b12f43ac43",
    #         "bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7",
    #         "5f07377b-cd67-4e8d-a834-ff485a9c3a9f",
    #         "7d3c8e2a-2295-4785-90a5-204007cc24fb",
    #         "2e1c2b51-c0d4-4de4-b3ab-460bc891e1d8"
    #     ]
    # )

    # Tests of updating (rename some row in db before)
    # is_in_vectorstore(collection=collection, ids="bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7")

    # synchronize_embeddings(
    #     nom_db_con_str=demo_stand_db_con_str,
    #     table_name=demo_stand_table_name,
    #     chroma_collection_name=demo_stand_chroma_collection_name,
    #     sync_period=24,
    # )

    # is_in_vectorstore(collection=collection, ids="bf937a2d-0c1d-4e9c-96f2-39d7c58e6fe7")
    pass
