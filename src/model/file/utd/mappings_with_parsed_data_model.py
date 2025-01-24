from typing import Any

from scheme.file.utd_card_message_scheme import MappedMaterial
from scheme.mapping.mapping_scheme import MappingNomenclaturesResultRead


def add_parsed_data_to_mappings(
    mapping_results: list[MappingNomenclaturesResultRead],
    # TODO: set type for 'parsed_materials_data'
    parsed_materials_data: list,
) -> list[MappedMaterial] | None:
    output_materials: list[MappedMaterial] = []

    # TODO: remove this later
    # It's needed just to set equal length for both lists
    parsed_materials_data = list(range(len(mapping_results)))

    for result, parsed_data in zip(mapping_results, parsed_materials_data):
        result: MappingNomenclaturesResultRead
        # TODO: fix 'parsed_data' type
        parsed_data: Any

        if result.nomenclatures is None:
            return None

        for nom in result.nomenclatures:
            nomenclature_guid = None
            if nom.mappings is not None and len(nom.mappings) > 0:
                nomenclature_guid = nom.mappings[0].material_code

            output_materials.append(
                MappedMaterial(
                    number=nom.row_number,
                    material_guid=nomenclature_guid,
                    idn_material_name=nom.nomenclature,
                    # similar_mappings=nom.similar_mappings,
                    # TODO: set parsed material data from 'parsed_data'
                    # ! Now it's mocked data
                    quantity=0.0,
                    price=0.0,
                    cost=0.0,
                    vat_rate=0.0,
                    vat_amount=0.0,
                )
            )

    return output_materials
