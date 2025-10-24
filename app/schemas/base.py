import datetime
from uuid import UUID

from pydantic import ConfigDict, BaseModel


class BasePydanticModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime.datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
        str_strip_whitespace=True,
        validate_assignment=True,
    )
