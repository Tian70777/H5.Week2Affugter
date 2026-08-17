"""Hvad Arduinoen maa sende. FastAPI afviser automatisk alt andet."""
from pydantic import BaseModel


class Reading(BaseModel):
    humidity: float
    temperature: float
    plug_on: bool


class SwitchEvent(BaseModel):
    turned_on: bool
    reason: str
    humidity: float
