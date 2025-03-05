from fastapi import HTTPException, status

from repository.mapping import mapping_iteration_repository
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration
from util.dates import get_now_utc


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
    try:
        # Try to get iteration by id
        db_iteration = get_iteration_by_id(iteration_id=iteration.id)

        # Update iteration
        db_iteration.metadatas = iteration.metadatas
        db_iteration.type = iteration.type
        db_iteration.status = iteration.status
        # Just to now catch error with JSON and datetime
        iteration = mapping_iteration_repository.update_iteration(
            iteration=db_iteration,
        )
    except HTTPException:
        # Create iteration if not exists to not lose results
        iteration.created_at = get_now_utc()
        iteration = mapping_iteration_repository.create_iteration(
            iteration=iteration,
        )

    return iteration
