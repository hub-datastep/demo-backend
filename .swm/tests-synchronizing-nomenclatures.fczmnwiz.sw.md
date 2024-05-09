---
title: '[TESTs] Synchronizing nomenclatures'
---
<SwmPath>[tests/synchronize_nomenclatures_model.test.py](/tests/synchronize_nomenclatures_model.test.py)</SwmPath>

### Скрипт для тестирования синхронизации на Демо-стенде.

**Как работает скрипт:**

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="204">

---

Он дропает таблицу **"СправочникНоменклатура"** и схему **"us"**, если такие существуют.

```python
    print(f"Dropping test table: {demo_stand_schema}.{demo_stand_table_name} ...")
    _drop_test_nomenclature_table(demo_stand_table_name, demo_stand_schema)
    print(f"Table dropped.")
```

---

</SwmSnippet>

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="208">

---

Потом создаёт их снова и заполняет таблицу тестовыми номенклатурами (10 штук).

```python
    print(f"Creating test table: {demo_stand_schema}.{demo_stand_table_name} ...")
    _create_test_nomenclature_table(demo_stand_table_name, demo_stand_schema)
    print(f"Table created.")

    print(f"Creating test noms...")
    _create_test_noms(demo_stand_table_name, demo_stand_schema)
    print(f"Noms created.")
```

---

</SwmSnippet>

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="221">

---

Также, он подключается к векторстору **(ChromaDB)** и удаляет тестовые векторы.

```python
    # Clear chroma from test noms & groups
    print(f"Clear test embeddings before tests...")
    delete_embeddings(
        collection=collection,
        ids=all_noms_guids
    )
    print(f"Test embeddings cleared.")
```

---

</SwmSnippet>

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="229">

---

После 1 теста, он должен создать 3 номенклатуры в векторсторе.

```python
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
```

---

</SwmSnippet>

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="241">

---

Дальше он обновляет некоторые номенклатуры.

```python
    print(f"Updating some noms...")
    _update_test_noms(demo_stand_table_name, demo_stand_schema)
    print(f"Noms updated...")
```

---

</SwmSnippet>

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="245">

---

И запускает ещё один тест, после которого он должен обновить 2 существующих вектора (эмбеддинга) и удалить 1.

```python
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
```

---

</SwmSnippet>

<SwmSnippet path="/tests/synchronize_nomenclatures_model.test.py" line="260">

---

По завершении, он просто удаляет тестовые эмбеддинги и дропает тестовую таблицу.

```python
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
```

---

</SwmSnippet>

<SwmMeta version="3.0.0" repo-id="Z2l0aHViJTNBJTNBbXN1LWJhY2tlbmQlM0ElM0FibGVzY2h1bm92" repo-name="msu-backend"><sup>Powered by [Swimm](https://app.swimm.io/)</sup></SwmMeta>
