from scheme.file.utd_card_message_scheme import MappedMaterial, MaterialWithParams
from scheme.mapping.mapping_scheme import (
    MappingNomenclaturesResultRead,
    MappingOneNomenclatureRead,
)


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

    mappings_list = mapped_nom.mappings
    similar_mappings_list = mapped_nom.mappings
    if mappings_list:
        material_guid = mappings_list[0].material_code
    # Set material guid from similar mappings
    elif similar_mappings_list:
        material_guid = similar_mappings_list[0].material_code

    return material_guid


def add_parsed_data_to_mappings(
    parsed_materials: list[MaterialWithParams],
    mapping_results: list[MappingNomenclaturesResultRead],
) -> list[MappedMaterial] | None:
    # Get all nomenclatures from mapping results
    mapped_noms_list: list[MappingOneNomenclatureRead] = []
    for nom in mapping_results:
        if nom.nomenclatures is not None:
            mapped_noms_list.extend(nom.nomenclatures)

    # Add mappings data to materials
    output_materials: list[MappedMaterial] = []
    for material in parsed_materials:
        # Find material in mapping results
        mapped_nom = _get_material_mapping_result(
            mapped_noms_list=mapped_noms_list,
            material=material,
        )

        # Get number from mapped nomenclature
        nom_number = -1
        material_guid = "-1"
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
