from typing import Any, Dict, Optional

from pydantic import BaseModel, ValidationInfo, field_validator


class OutputSchema(BaseModel):
    sub: str
    name: Optional[str]
    family_name: Optional[str]
    given_name: Optional[str]
    middle_name: Optional[str]
    nickname: Optional[str]
    preferred_username: Optional[str]
    profile: Optional[str]
    picture: Optional[str]
    website: Optional[str]
    gender: Optional[str]
    birthdate: Optional[str]
    zoneinfo: Optional[str]
    locale: Optional[str]
    updated_at: Optional[int]
    address: Optional[Dict[str, Any]]
    email: Optional[str]
    phone_number: Optional[str]

    # バリデータを使用して、フィールドの最大長を指定
    @field_validator(
        "name",
        "family_name",
        "given_name",
        "middle_name",
        "nickname",
        "preferred_username",
        "profile",
        "picture",
        "website",
        "gender",
        "zoneinfo",
        "locale",
        "email",
        "phone_number",
        mode="after",
    )
    def validate_length(cls, v, info: ValidationInfo):
        if isinstance(v, str):
            # フィールドごとの最大長を定義
            max_len_dict = {
                "name": 12,
                "family_name": 12,
                "given_name": 12,
                "middle_name": 12,
                "nickname": 12,
                "preferred_username": 20,
                "profile": 256,
                "picture": 256,
                "website": 256,
                "gender": 10,
                "zoneinfo": 64,
                "locale": 10,
                "email": 256,
                "phone_number": 15,
            }
            field_name = info.field_name
            max_len = max_len_dict.get(field_name, 256)

            if len(v) > max_len:
                sub = info.data.get("sub", "unknown")
                print(
                    f"Warning: field '{field_name}' in item '{sub}' exceeded max length of {max_len} characters and was truncated."
                )

                return v[:max_len]
        return v
