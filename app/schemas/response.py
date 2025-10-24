from pydantic import BaseModel, Field
from typing import Any, TypeVar, Generic, Sequence

DataT = TypeVar("DataT")


class ApiResponseSchema(BaseModel, Generic[DataT]):
    data: DataT | dict = Field(
        default_factory=dict,
        description="Response data payload.",
    )
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the response",
    )
    errors: Sequence[Any] = Field(
        default_factory=list,
        description="List of errors, empty if successful",
    )
