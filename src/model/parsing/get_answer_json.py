def get_materials_into_mapping(mapping_nomenclatures:list[dict]):
    out = []
    for job in mapping_nomenclatures:
        for nomenclature in job['nomenclatures']:
            out.append({
                "number": nomenclature['row_number'] + 1,
                "material_guid": "zaglyshka",
                "idn_material_name": nomenclature['mappings'],
                "similar_mappings" : [
                    {
                        "nomenclature_guid": similar['nomenclature_guid'],  # Оставляем как строку
                        "nomenclature": similar['nomenclature'],
                        "similarity_score": similar['similarity_score']
                    }
                for similar in nomenclature['similar_mappings'] or [] if nomenclature['mappings'] is None # Защита от отсутствующих значений
                ],
                "quantity":16.25,  # Значение из вашего примера
                "price":100.00,    # Значение из вашего примера
                "cost":1625.00,    # Значение из вашего примера
                "vat_rate":20.00,  # Значение из вашего примера
                "vat_amount":1946.40  # Значение из вашего примера
            })
    return out


if __name__=="__main__":
    v = [{'job_id': 'd89d523e-be2e-4621-a648-ec3d743a85fc', 'ready_count': 2, 'total_count': 2, 'general_status': 'finished', 'nomenclatures': [{'row_number': 0, 'nomenclature': 'Труба ПЭ100 SDR11 - 200х18,2 питьевая (12м)', 'group': 'Водоснабжение и Канализация', 'nomenclature_params': [{'overall_size_mm_cm_m': '12м'}, {'rectangular_dimensions': '200-18-2'}], 'mappings': 'Труба ПЭ100 SDR11-200х18,2 питьевая', 'similar_mappings': [{'nomenclature_guid': '1948', 'nomenclature': 'Труба ПЭ100 SDR11-200х18,2 питьевая', 'similarity_score': 0.03789564222097397}, {'nomenclature_guid': '1977', 'nomenclature': 'Труба ПЭ100 SDR17-200х11,9 питьевая', 'similarity_score': 0.10369685292243958}, {'nomenclature_guid': '1984', 'nomenclature': 'Труба ПЭ100 SDR21-110х5,2', 'similarity_score': 0.1350041776895523}]}, {'row_number': 1, 'nomenclature': 'Лестничный марш ЛМФ 30-11-14,5', 'group': 'Лестничные марши и площадки железобетонные Материалы', 'nomenclature_params': [{'rectangular_dimensions': '30-11-14'}], 'mappings': [{'nomenclature_guid': '1725', 'nomenclature': 'ЛМФ 30-11-14,5', 'similarity_score': 0.10306374728679657}], 'similar_mappings': None}]}]
    print(get_materials_into_mapping(v))
