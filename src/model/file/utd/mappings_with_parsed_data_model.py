from scheme.file.utd_card_message_scheme import MappedMaterial, MaterialWithParams
from scheme.mapping.mapping_scheme import (
    MappingNomenclaturesResultRead,
    MappingOneNomenclatureRead,
)


def extract_results_from_mapping_jobs(
    mapping_jobs: list[MappingNomenclaturesResultRead],
) -> list[MappingOneNomenclatureRead]:
    """
    Вытаскивает из джоб маппинга результаты и собирает их в единый список.
    """

    mapped_noms_list: list[MappingOneNomenclatureRead] = []
    for job in mapping_jobs:
        nom_results = job.nomenclatures
        if nom_results is not None:
            mapped_noms_list.extend(nom_results)
    return mapped_noms_list


def _get_material_mapping_result(
    mapped_noms_list: list[MappingOneNomenclatureRead],
    material: MaterialWithParams,
) -> MappingOneNomenclatureRead | None:
    mapped_nom: MappingOneNomenclatureRead | None = None

    for result in mapped_noms_list:
        if result.nomenclature == material.idn_material_name:
            mapped_nom = result
            break

    return mapped_nom


def _get_material_code_from_mappings(
    mapped_nom: MappingOneNomenclatureRead,
) -> str | None:
    material_guid: str | None = None

    # Get code from mappings & similar mapping
    mappings_list = mapped_nom.mappings
    similar_mappings_list = mapped_nom.similar_mappings
    if mappings_list:
        material_guid = mappings_list[0].material_code
    # Set material guid from similar mappings
    elif similar_mappings_list:
        material_guid = similar_mappings_list[0].material_code

    return material_guid


def add_parsed_data_to_mappings(
    parsed_materials: list[MaterialWithParams],
    mapping_results: list[MappingOneNomenclatureRead],
) -> list[MappedMaterial] | None:
    # Add mappings data to materials
    output_materials: list[MappedMaterial] = []
    for material in parsed_materials:
        # Find material in mapping results
        mapped_nom = _get_material_mapping_result(
            mapped_noms_list=mapping_results,
            material=material,
        )

        # Get number from mapped nomenclature
        nom_number: int = -1
        material_guid: str | None = None
        if mapped_nom:
            # Get material number
            nom_number = mapped_nom.row_number

            # Get material guid from mapped nomenclature
            material_guid = _get_material_code_from_mappings(
                mapped_nom=mapped_nom,
            )

        output_materials.append(
            MappedMaterial(
                **material.dict(),
                number=nom_number,
                material_guid=material_guid,
            )
        )

    return output_materials
