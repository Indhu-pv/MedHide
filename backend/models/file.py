from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileUpload(BaseModel):
    file_id: str
    file_name: str
    message: str
    key: str

class LabFile(BaseModel):
    file_id: str
    file_name: str
    lab_id: str
    lab_name: str
    lab_email: str
    role: str
    date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "uploaded"  # uploaded, requested, decrypted
    key: str
    image_path: Optional[str] = None

class Request(BaseModel):
    fid: str
    fname: str
    owner_name: str
    rid: str
    rname: str
    remail: str
    date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"