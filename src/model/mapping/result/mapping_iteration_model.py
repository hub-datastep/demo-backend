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


def create_or_update_iteration(
    iteration: MappingIteration,
) -> MappingIteration:
    iteration: MappingIteration | None = None

    try:
        # Try to get iteration by id
        db_iteration = get_iteration_by_id(iteration_id=iteration.id)

        # Update iteration
        db_iteration.metadatas = iteration.metadatas
        db_iteration.type = iteration.type
        iteration = mapping_iteration_repository.update_iteration(
            iteration=db_iteration,
        )
    except HTTPException:
        # Create iteration if not exists to not lose results
        iteration = mapping_iteration_repository.create_iteration(
            iteration=iteration,
        )

    return iteration
