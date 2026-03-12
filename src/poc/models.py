from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any


class DeviceInfo(BaseModel):
    name: str
    os: str
    description: str


class Asset(BaseModel):
    name: str
    description: str
    type: Literal["security", "network"]
    dt: Dict[str, Any]


class DeviceConfig(BaseModel):
    info: DeviceInfo
    assets: List[Asset] = Field(min_length=1)
