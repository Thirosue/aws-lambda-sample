from pydantic import BaseModel, field_validator


class InputSchema(BaseModel):
    first_name: str
    last_name: str
    deleted: int

    @field_validator("deleted")
    def validate_deleted(cls, v: int) -> int:
        if v not in [0, 1]:
            raise ValueError("Deleted must be 0 or 1")
        return v


class OutPutSchema(BaseModel):
    name: str
    is_deleted: int
