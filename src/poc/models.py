from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any

# Modelli pydantic per la validazione del file JSON in input.
# Definiscono la strutura attesa di "info", "assets". DeviceConfig rappresenta il livello principale: raggruppa info + asset


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
