from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DirectoryOut(BaseModel):
    # model_config = ConfigDict(from_attributes=True)

    dir_name: str
    owner_id: int
    created_at: datetime
    owner:str

class FileOut(BaseModel):
    file_name: str
    content_type: str
    created_at: datetime

    owner_id: int
    owner: str
    parent: DirectoryOut

    model_config = ConfigDict(from_attributes=True)
