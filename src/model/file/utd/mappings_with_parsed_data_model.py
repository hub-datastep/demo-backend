from typing import Any

from scheme.file.utd_card_message_scheme import MappedMaterial
from scheme.mapping.mapping_scheme import MappingNomenclaturesResultRead


def add_parsed_data_to_mappings(
    mapping_results: list[MappingNomenclaturesResultRead],
    # TODO: set type for 'parsed_materials_data'
    parsed_materials_data: list,
):
    output_materials: list[MappedMaterial] = []

    for result, parsed_material in zip(mapping_results, parsed_materials_data):
        result: MappingNomenclaturesResultRead
        # TODO: fix 'parsed_material' type
        parsed_material: Any

        for nom in result.nomenclatures:
            output_materials.append(
                MappedMaterial(
                    number=nom.row_number,
                    # TODO: replace 'nomenclature_guid' from vectorstore to guid from НСИ
                    material_guid=nom.mappings[0].nomenclature_guid,
                    similar_mappings=nom.similar_mappings,
                    # TODO: set parsed material data
                    # idn_material_name=parsed_material.,
                    # quantity=material_parsed_data.,
                    # price=material_parsed_data.,
                    # cost=material_parsed_data.,
                    # vat_rate=material_parsed_data.,
                    # vat_amount=material_parsed_data.,
                )
            )

    return output_materials
