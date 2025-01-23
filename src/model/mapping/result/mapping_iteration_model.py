from fastapi import HTTPException, status

from repository.mapping import mapping_iteration_repository
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration


def get_iteration_by_id(
    iteration_id: str,
) -> MappingIteration:
    iteration = mapping_iteration_repository.get_iteration_by_id(
        iteration_id=iteration_id,
    )

    if not iteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping Iteration with ID '{iteration_id}' not found",
        )

    return iteration
