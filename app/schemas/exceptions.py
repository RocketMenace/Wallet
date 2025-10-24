from pydantic import BaseModel, Field


class CoreServiceExceptionSchema(BaseModel):
    detail: str = Field(..., description="Exception detail")
    message: str = Field(..., description="A human-readable explanation of the error")
