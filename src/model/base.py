from typing import Generic, TypeVar

from fastapi import HTTPException, status
from sqlmodel import SQLModel

from repository.base import BaseRepository

ModelType = TypeVar("ModelType", bound=SQLModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseModel(Generic[ModelType, RepositoryType]):
    """
    A base model class for interacting with the database using a repository pattern.

    This class serves as a wrapper around a provided repository, allowing higher-level
    methods for CRUD operations and additional functionality such as error handling.
    """

    def __init__(
        self,
        schema: type[ModelType],
        repository: RepositoryType,
    ) -> None:
        """
        Initialize the BaseModel instance.

        :param schema: The SQLModel schema representing the database table.
        :param repository: A custom repository instance for database operations.
        """

        self.schema = schema
        self.repository = repository

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record in the database table.

        :param obj: The instance of the model to save.
        :return: The saved object with updated fields (e.g., ID).
        """

        return await self.repository.create(obj=obj)

    async def get_by_id(self, obj_id: int) -> ModelType | None:
        """
        Retrieve a single record by its ID.

        :param obj_id: The ID of the record to retrieve.
        :return: The object if found, otherwise raises an HTTPException with a 404 status code.
        :raises HTTPException: If the object with the given ID is not found.
        """

        obj = await self.repository.get_by_id(obj_id=obj_id)

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.schema.__name__} with ID {obj_id} not found",
            )

        return obj

    async def get_all(self) -> list[ModelType]:
        """
        Retrieve all records from the database table.

        :return: A list of all objects in the table.
        """

        return await self.repository.get_all()

    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record in the database table.

        :param obj: The instance of the model with updated data.
        :return: The updated object after saving changes.
        :raises HTTPException: If the object to update does not exist.
        """

        # Check if obj exists
        await self.repository.get_by_id(obj_id=obj.id)

        return await self.repository.update(obj=obj)

    async def delete(self, obj: ModelType) -> None:
        """
        Delete a record from the database table.

        :param obj: The instance of the model to delete.
        :raises HTTPException: If the object to delete does not exist.
        """

        # Check if obj exists
        await self.repository.get_by_id(obj_id=obj.id)

        return await self.repository.delete(obj=obj)
