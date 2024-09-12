from model.mapping.mapping_model import build_where_metadatas

test_group = "electronics"
test_brand = "sony"
test_metadatas_list_many = [
    {"param1": "value1"},
    {"param2": "value2"},
]
test_metadatas_list_one = [
    {"param1": "value1"},
]


# 1. Тест жесткого поиска с параметрами и брендом
def test_hard_search_with_params_and_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=True,
        is_brand_needed=True,
        is_hard_params=True
    )
    assert result == {
        "$and": [
            {"group": "electronics"},
            {"param1": "value1"},
            {"param2": "value2"},
            {"brand": "sony"}
        ]
    }


# 2. Тест жесткого поиска с параметрами без бренда
def test_hard_search_with_params_no_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=True,
        is_brand_needed=False,
        is_hard_params=True
    )
    assert result == {
        "$and": [
            {"group": "electronics"},
            {"param1": "value1"},
            {"param2": "value2"}
        ]
    }


# 3. Тест жесткого поиска без параметров, с брендом
def test_hard_search_no_params_with_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=False,
        is_brand_needed=True,
        is_hard_params=True
    )
    assert result == {
        "$and": [
            {"group": "electronics"},
            {"brand": "sony"}
        ]
    }


# 4. Тест жесткого поиска без параметров и без бренда
def test_hard_search_no_params_no_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=False,
        is_brand_needed=False,
        is_hard_params=True
    )
    assert result == {"group": "electronics"}


# 5. Тест мягкого поиска с параметрами и брендом
def test_soft_search_with_params_and_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=True,
        is_brand_needed=True,
        is_hard_params=False
    )
    assert result == {
        "$and": [
            {"group": "electronics"},
            {
                "$or": [
                    {"param1": "value1"},
                    {"param2": "value2"},
                    {"brand": "sony"}
                ]
            }
        ]
    }


# 6. Тест мягкого поиска с одним параметром, без бренда
def test_soft_search_one_param_no_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_one,
        is_params_needed=True,
        is_brand_needed=False,
        is_hard_params=False
    )
    assert result == {
        "$or": [
            {"group": "electronics"},
            {
                "$and": [
                    {"group": "electronics"},
                    {"param1": "value1"}
                ]
            }
        ]
    }


# 7. Тест мягкого поиска с параметрами без бренда
def test_soft_search_with_params_no_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=True,
        is_brand_needed=False,
        is_hard_params=False
    )
    assert result == {
        "$and": [
            {"group": "electronics"},
            {
                "$or": [
                    {"param1": "value1"},
                    {"param2": "value2"}
                ]
            }
        ]
    }


# 8. Тест мягкого поиска без параметров, с брендом
def test_soft_search_no_params_with_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=False,
        is_brand_needed=True,
        is_hard_params=False
    )
    assert result == {
        "$or": [
            {"group": "electronics"},
            {
                "$and": [
                    {"group": "electronics"},
                    {"brand": "sony"}
                ]
            }
        ]
    }


# 9. Тест мягкого поиска без параметров и без бренда
def test_soft_search_no_params_no_brand():
    result = build_where_metadatas(
        group=test_group,
        brand=test_brand,
        metadatas_list=test_metadatas_list_many,
        is_params_needed=False,
        is_brand_needed=False,
        is_hard_params=False
    )
    assert result == {"group": "electronics"}
