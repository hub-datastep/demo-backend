from datetime import datetime
from uuid import uuid4

from model.nomenclature.synchronize_nomenclatures_model import get_chroma_patch_for_sync
from scheme.mapping.mapping_scheme import MsuDatabaseOneNomenclatureRead, SyncOneNomenclatureDataRead, \
    SyncNomenclaturesChromaPatch

"""
Логика в get_chroma_patch_for_sync зависит от трёх параметров: root_group_name, is_in_vectorstore, is_deleted.
Проверим все их сочетания.

000, 001, 010, 011, 100, 101, 110, 111
0002 False False, 0002 False True, 0002 True False, 0002 True True
0001 False False, 0001 False True, 0001 True False, 0001 True True
"""


def test_1():
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
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
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
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
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0002 ...",
            is_in_vectorstore=True,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesChromaPatch(
        nomenclature_data=SyncOneNomenclatureDataRead(id=id_, nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_4():
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0002 ...",
            is_in_vectorstore=True,
            is_deleted=True,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesChromaPatch(
        nomenclature_data=SyncOneNomenclatureDataRead(id=id_, nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_5():
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=False,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = []
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_6():
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
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
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=True,
            is_deleted=False,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesChromaPatch(
        nomenclature_data=SyncOneNomenclatureDataRead(id=id_, nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers


def test_8():
    id_ = str(uuid4())
    test_data = [
        MsuDatabaseOneNomenclatureRead(
            id=id_, nomenclature_name="Циркуль", group="Канцелярия",
            root_group_name="0001 Новая структура справочника",
            is_in_vectorstore=True,
            is_deleted=True,
            edited_at=datetime.now(),
            is_group=False
        )
    ]
    test_answers = [SyncNomenclaturesChromaPatch(
        nomenclature_data=SyncOneNomenclatureDataRead(id=id_, nomenclature_name="Циркуль", group="Канцелярия"),
        action="delete"
    )]
    assert get_chroma_patch_for_sync(test_data) == test_answers
