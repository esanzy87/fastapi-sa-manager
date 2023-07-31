from typing import Generic, TypeVar
from pydantic import BaseModel as BaseSchema
from pydantic.generics import GenericModel


ListItemT = TypeVar("ListItemT", bound=BaseSchema)


class PaginatedList(GenericModel, Generic[ListItemT]):
    total_count: int
    results: list[ListItemT]
    page: int
    per_page: int
