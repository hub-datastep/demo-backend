from typing import Generic, TypeVar

from sqlalchemy.sql.ddl import CreateSchema
from sqlmodel import SQLModel, select

from infra.async_database import engine, get_session
from middleware.error_handle_middleware import handle_errors

SchemaType = TypeVar("SchemaType", bound=SQLModel)


class BaseRepository(Generic[SchemaType]):
    """
    Generic base repository for CRUD operations on DB table.

    This class provides methods to interact with DB using SQLModel schemas.
    It is designed to be extended or used as-is for basic DB operations.

    Attributes:
        schema (type[SchemaType]): The SQLModel schema representing the DB table.
    """

    def __init__(self, schema: type[SchemaType]) -> None:
        """
        Initialize base repository with the given schema.

        Args:
            schema (type[SchemaType]): SQLModel schema representing DB table.
        """

        self.schema = schema
        self.get_session = get_session
        self.engine = engine

    @handle_errors
    async def get_all(self) -> list[SchemaType]:
        """
        Get all objects from DB table.

        Returns:
            list[SchemaType]: List of all objects in DB table.
        """

        async with self.get_session() as session:
            st = select(self.schema)
            result = await session.exec(st)
            return list(result.all())

    @handle_errors
    async def get_by_id(self, obj_id: int) -> SchemaType | None:
        """
        Get first object by its ID.

        Args:
            obj_id (int): ID of object to get.

        Returns:
            SchemaType | None: Object if found, else None.
        """

        async with self.get_session() as session:
            st = select(self.schema)
            st = st.where(self.schema.id == obj_id)
            result = await session.exec(st)
            return result.first()

    @handle_errors
    async def create(self, obj: SchemaType) -> SchemaType:
        """
        Create new object in DB table.

        Args:
            obj (SchemaType): Instance of model to create.

        Returns:
            SchemaType: Saved object with ID.
        """

        async with self.get_session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @handle_errors
    async def update(self, obj: SchemaType) -> SchemaType:
        """
        Update existing object in DB table.

        Args:
            obj (SchemaType): Instance of model with updated data.

        Returns:
            SchemaType: Updated object.
        """

        async with self.get_session() as session:
            db_obj = await session.merge(obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    @handle_errors
    async def delete(self, obj: SchemaType) -> None:
        """
        Delete a object from DB table.

        Args:
            obj (SchemaType): Instance of model to delete.
        """

        async with self.get_session() as session:
            await session.delete(obj)
            await session.commit()

    @handle_errors
    async def create_schema_and_table(
        self,
        schema: str | None = None,
    ):
        # Set table schema
        SchemaType.__table__.schema = schema

        # Create schema for history table if not exists
        with self.get_session() as session:
            session.exec(
                CreateSchema(
                    name=schema,
                    if_not_exists=True,
                )
            )
            session.commit()

        # Create table if not exists
        SchemaType.metadata.create_all(self.engine)
