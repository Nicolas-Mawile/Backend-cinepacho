"""Abstract repository base class."""

from typing import Generic, TypeVar

T = TypeVar("T")


class AbstractRepository(Generic[T]):
    async def add(self, entity: T) -> T:
        raise NotImplementedError

    async def get(self, entity_id: int) -> T:
        raise NotImplementedError

    async def list(self) -> list[T]:
        raise NotImplementedError

    async def remove(self, entity: T) -> None:
        raise NotImplementedError
