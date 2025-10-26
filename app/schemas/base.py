from pydantic import ConfigDict, BaseModel


class BasePydanticModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )
