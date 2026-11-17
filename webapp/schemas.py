import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TelegramLogin(StrictModel):
    init_data: str = Field(min_length=1, max_length=16384)


class LeadCreate(StrictModel):
    full_name: str = Field(min_length=3, max_length=100)
    phone: str = Field(min_length=9, max_length=30)
    age: int = Field(ge=7, le=90)
    region: str = Field(min_length=2, max_length=200)
    course_id: int = Field(gt=0)
    time_preference: Literal["Ertalab", "Tushdan keyin", "Kechki", "Farqi yo‘q"]
    kind: Literal["course", "trial"] = "course"

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value):
        value = re.sub(r"[\s()\-]", "", value)
        if not re.fullmatch(r"\+?998\d{9}", value):
            raise ValueError("Telefon +998 va 9 ta raqamdan iborat bo‘lsin.")
        return "+" + value.lstrip("+")


class LeadUpdate(StrictModel):
    status: Literal["YANGI", "BOGLANILDI", "YOZILDI", "BEKOR_QILINDI"]
    sales_notes: str = Field(default="", max_length=2000)
    updated_at: str = Field(min_length=1, max_length=80)


class CourseWrite(StrictModel):
    name: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=2500)
    duration: str = Field(min_length=1, max_length=60)
    price: str = Field(min_length=1, max_length=80)
    technologies: str = Field(default="", max_length=500)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0, le=10000)


class SalesWrite(StrictModel):
    telegram_id: int = Field(gt=0, lt=2**63)
    full_name: str = Field(min_length=3, max_length=100)
    phone: str = Field(default="", max_length=30)


class FeedbackWrite(StrictModel):
    message: str = Field(min_length=5, max_length=3000)


class SettingsWrite(StrictModel):
    values: dict[str, str]


class QuizAnswers(StrictModel):
    answers: list[int] = Field(min_length=5, max_length=5)

    @field_validator("answers")
    @classmethod
    def check_choices(cls, values):
        if any(type(n) is not int or n not in range(4) for n in values):
            raise ValueError("Har bir savolda bitta javob tanlang.")
        return values


class BroadcastWrite(StrictModel):
    message: str = Field(min_length=1, max_length=4096)
    upload_id: str | None = Field(default=None, max_length=40)
    confirmed: Literal[True]
    request_key: str = Field(min_length=16, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
