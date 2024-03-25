from datetime import datetime

from model.synchronize_nomenclatures_model import get_chroma_patch_for_sync
from scheme.nomenclature_scheme import MsuDatabaseOneNomenclatureRead, SyncOneNomenclature, SyncNomenclaturesPatch

"""
Логика в get_chroma_patch_for_sync зависит от трёх параметров: root_group_name, is_in_vectorstore, is_deleted.
Проверим все их сочетания.

000, 001, 010, 011, 100, 101, 110, 111
0002 False False, 0002 False True, 0002 True False, 0002 True True
0001 False False, 0001 False True, 0001 True False, 0001 True True
"""


def test_1():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="1", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0002 ...",
            is_in_vectorstore=False,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = []
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_2():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="2", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0002 ...",
            is_in_vectorstore=False,
            is_deleted=True,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = []
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_3():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="3", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0002 ...",
            is_in_vectorstore=True,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesPatch(
        nomenclature_data=SyncOneNomenclature(id="3", nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_4():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="4", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0002 ...",
            is_in_vectorstore=True,
            is_deleted=True,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesPatch(
        nomenclature_data=SyncOneNomenclature(id="4", nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_5():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="5", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=False,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesPatch(
        nomenclature_data=SyncOneNomenclature(id="5", nomenclature_name="Циркуль", group="Канцелярия"),
        action="create"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_6():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="6", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=False,
            is_deleted=True,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = []
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_7():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="7", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=True,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesPatch(
        nomenclature_data=SyncOneNomenclature(id="7", nomenclature_name="Циркуль", group="Канцелярия"),
        action="update"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_8():
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id="8", nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=True,
            is_deleted=True,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesPatch(
        nomenclature_data=SyncOneNomenclature(id="8", nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers
