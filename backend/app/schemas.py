from pydantic import BaseModel, ConfigDict
from typing import Optional

class ModuleOut(BaseModel):
    id: int
    code: str
    name: str
    description: str
    model_config = ConfigDict(from_attributes=True)

class DeviceCreate(BaseModel):
    code: str
    name: str
    module_id: int
    description: str = ""
    function: str = ""
    image_path: str = ""
    model3d_path: str = ""
    video_path: str = ""

class DeviceOut(DeviceCreate):
    id: int
    qr_path: str
    active: bool
    model_config = ConfigDict(from_attributes=True)
